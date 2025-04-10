#!/usr/bin/env python3
"""
NOVAXA Monitoring Script
This script checks the health of the NOVAXA Telegram bot and web dashboard
and sends alerts if any issues are detected.
"""

import os
import sys
import time
import logging
import requests
import json
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("monitoring.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("novaxa_monitor")

# Default configuration
DEFAULT_CONFIG = {
    "bot_url": "https://novaxa-telegram-bot.onrender.com",
    "dashboard_url": "https://novaxa-dashboard.onrender.com",
    "check_interval": 300,  # 5 minutes
    "alert_threshold": 3,   # Number of consecutive failures before alerting
    "telegram_chat_id": None,
    "bot_token": os.getenv("BOT_TOKEN")
}

class NOVAXAMonitor:
    def __init__(self, config=None):
        """Initialize the monitor with configuration"""
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        
        self.failure_count_bot = 0
        self.failure_count_dashboard = 0
        self.last_alert_time = 0
        
        logger.info("NOVAXA Monitor initialized")
        logger.info(f"Bot URL: {self.config['bot_url']}")
        logger.info(f"Dashboard URL: {self.config['dashboard_url']}")
        logger.info(f"Check interval: {self.config['check_interval']} seconds")
        
        # Validate configuration
        if self.config.get("telegram_chat_id") and not self.config.get("bot_token"):
            logger.warning("Telegram chat ID is set but bot token is missing. Alerts will not be sent via Telegram.")
    
    def check_bot_health(self):
        """Check the health of the Telegram bot"""
        try:
            url = f"{self.config['bot_url']}/health"
            logger.info(f"Checking bot health at {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Bot health check: OK")
                self.failure_count_bot = 0
                return True
            else:
                logger.error(f"Bot health check failed with status code: {response.status_code}")
                self.failure_count_bot += 1
                return False
        except Exception as e:
            logger.error(f"Bot health check error: {str(e)}")
            self.failure_count_bot += 1
            return False
    
    def check_dashboard_health(self):
        """Check the health of the web dashboard"""
        try:
            url = f"{self.config['dashboard_url']}/health"
            logger.info(f"Checking dashboard health at {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Dashboard health check: OK")
                self.failure_count_dashboard = 0
                return True
            else:
                logger.error(f"Dashboard health check failed with status code: {response.status_code}")
                self.failure_count_dashboard += 1
                return False
        except Exception as e:
            logger.error(f"Dashboard health check error: {str(e)}")
            self.failure_count_dashboard += 1
            return False
    
    def send_alert(self, message):
        """Send an alert about service issues"""
        logger.warning(f"ALERT: {message}")
        
        # Avoid sending too many alerts
        current_time = time.time()
        if current_time - self.last_alert_time < 3600:  # 1 hour
            logger.info("Skipping alert notification (rate limited)")
            return
        
        self.last_alert_time = current_time
        
        # Send Telegram alert if configured
        if self.config.get("telegram_chat_id") and self.config.get("bot_token"):
            try:
                telegram_url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"
                data = {
                    "chat_id": self.config["telegram_chat_id"],
                    "text": f"🚨 NOVAXA Monitor Alert 🚨\n\n{message}\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "parse_mode": "Markdown"
                }
                
                response = requests.post(telegram_url, json=data, timeout=10)
                
                if response.status_code == 200:
                    logger.info("Alert sent via Telegram")
                else:
                    logger.error(f"Failed to send Telegram alert: {response.text}")
            except Exception as e:
                logger.error(f"Error sending Telegram alert: {str(e)}")
    
    def run(self):
        """Run the monitoring loop"""
        logger.info("Starting monitoring loop")
        
        try:
            while True:
                # Check bot health
                bot_healthy = self.check_bot_health()
                
                # Check dashboard health
                dashboard_healthy = self.check_dashboard_health()
                
                # Send alerts if needed
                if self.failure_count_bot >= self.config["alert_threshold"]:
                    self.send_alert(f"Telegram bot is down! Failed health checks: {self.failure_count_bot}")
                
                if self.failure_count_dashboard >= self.config["alert_threshold"]:
                    self.send_alert(f"Web dashboard is down! Failed health checks: {self.failure_count_dashboard}")
                
                # Log overall status
                logger.info(f"Status: Bot {'OK' if bot_healthy else 'FAIL'}, Dashboard {'OK' if dashboard_healthy else 'FAIL'}")
                
                # Wait for next check
                time.sleep(self.config["check_interval"])
        
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")
            self.send_alert(f"Monitoring service error: {str(e)}")

def load_config(config_file):
    """Load configuration from a JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config file: {str(e)}")
        return {}

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="NOVAXA Monitoring Script")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--bot-url", help="URL of the Telegram bot service")
    parser.add_argument("--dashboard-url", help="URL of the web dashboard service")
    parser.add_argument("--interval", type=int, help="Check interval in seconds")
    parser.add_argument("--chat-id", help="Telegram chat ID for alerts")
    parser.add_argument("--token", help="Telegram bot token")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Override with command line arguments
    if args.bot_url:
        config["bot_url"] = args.bot_url
    if args.dashboard_url:
        config["dashboard_url"] = args.dashboard_url
    if args.interval:
        config["check_interval"] = args.interval
    if args.chat_id:
        config["telegram_chat_id"] = args.chat_id
    if args.token:
        config["bot_token"] = args.token
    
    # Start monitoring
    monitor = NOVAXAMonitor(config)
    monitor.run()

if __name__ == "__main__":
    main()
