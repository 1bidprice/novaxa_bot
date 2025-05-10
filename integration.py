#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integration Module for Telegram Bot
-----------------------------------
Provides service integration and notification capabilities for the Enhanced Telegram Bot.

This module handles integration with external services and systems,
as well as notification management for the bot.
"""

import os
import sys
import logging
import json
import time
import requests
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable

# Import the Bot class from telegram for type hinting and sending messages
from telegram import Bot as TelegramBotInstance # Renamed to avoid conflict if Bot is used elsewhere

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class ServiceIntegration:
    """
    Handles integration with external services and APIs.
    
    This class provides methods for connecting to and interacting with
    various external services and systems.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the service integration handler.
        
        Args:
            config_file: Path to configuration file for service integrations
        """
        self.config = {}
        self.services = {}
        self.session = requests.Session()
        
        # Load configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        
        logger.info("Service integration initialized")
    
    def load_config(self, config_file: str) -> bool:
        """
        Load configuration from a file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            True if configuration was loaded successfully, False otherwise
        """
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            
            # Initialize services based on configuration
            for service_name, service_config in self.config.get("services", {}).items():
                if service_config.get("enabled", False):
                    self.services[service_name] = {
                        "config": service_config,
                        "status": "initialized",
                        "last_check": None,
                    }
            
            logger.info(f"Loaded configuration from {config_file}")
            logger.info(f"Enabled services: {', '.join(self.services.keys())}")
            return True
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    # ... (rest of ServiceIntegration class remains the same as you provided) ...
    # Make sure to include all methods from your original ServiceIntegration class here
    # For brevity, I am omitting the rest of ServiceIntegration, assuming it's correct.
    # Please ensure you copy the full ServiceIntegration class from your version.

    def save_config(self, config_file: str) -> bool:
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved configuration to {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False

    def register_service(self, service_name: str, service_config: Dict) -> bool:
        try:
            if "services" not in self.config:
                self.config["services"] = {}
            self.config["services"][service_name] = service_config
            if service_config.get("enabled", False):
                self.services[service_name] = {
                    "config": service_config,
                    "status": "initialized",
                    "last_check": None,
                }
            logger.info(f"Registered service: {service_name}")
            return True
        except Exception as e:
            logger.error(f"Error registering service: {e}")
            return False

    def enable_service(self, service_name: str) -> bool:
        if service_name not in self.config.get("services", {}):
            logger.error(f"Service not found: {service_name}")
            return False
        try:
            self.config["services"][service_name]["enabled"] = True
            self.services[service_name] = {
                "config": self.config["services"][service_name],
                "status": "initialized",
                "last_check": None,
            }
            logger.info(f"Enabled service: {service_name}")
            return True
        except Exception as e:
            logger.error(f"Error enabling service: {e}")
            return False

    def disable_service(self, service_name: str) -> bool:
        if service_name not in self.config.get("services", {}):
            logger.error(f"Service not found: {service_name}")
            return False
        try:
            self.config["services"][service_name]["enabled"] = False
            if service_name in self.services:
                del self.services[service_name]
            logger.info(f"Disabled service: {service_name}")
            return True
        except Exception as e:
            logger.error(f"Error disabling service: {e}")
            return False

    def get_service_status(self, service_name: str) -> Dict:
        if service_name not in self.services:
            return {
                "status": "disabled",
                "error": "Service not enabled",
            }
        return {
            "status": self.services[service_name].get("status", "unknown"),
            "last_check": self.services[service_name].get("last_check"),
            "config": {
                k: v for k, v in self.services[service_name].get("config", {}).items()
                if k not in ["api_key", "password", "secret", "token"]
            },
        }

    def check_service(self, service_name: str) -> Dict:
        if service_name not in self.services:
            return {
                "status": "disabled",
                "error": "Service not enabled",
            }
        service = self.services[service_name]
        service_config = service.get("config", {})
        service["last_check"] = datetime.now().isoformat()
        service_type = service_config.get("type", "")
        if service_type == "http":
            return self._check_http_service(service_name, service_config)
        elif service_type == "smtp":
            return self._check_smtp_service(service_name, service_config)
        elif service_type == "database":
            return self._check_database_service(service_name, service_config)
        else:
            service["status"] = "unknown"
            return {
                "status": "unknown",
                "error": f"Unknown service type: {service_type}",
            }

    def _check_http_service(self, service_name: str, service_config: Dict) -> Dict:
        url = service_config.get("url", "")
        method = service_config.get("method", "GET")
        headers = service_config.get("headers", {})
        timeout = service_config.get("timeout", 10)
        if not url:
            self.services[service_name]["status"] = "error"
            return {
                "status": "error",
                "error": "URL not specified",
            }
        try:
            start_time = time.time()
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
            )
            response_time = time.time() - start_time
            status_code = response.status_code
            if 200 <= status_code < 300:
                self.services[service_name]["status"] = "ok"
                return {
                    "status": "ok",
                    "response_time": response_time,
                    "status_code": status_code,
                }
            else:
                self.services[service_name]["status"] = "error"
                return {
                    "status": "error",
                    "error": f"HTTP error: {status_code}",
                    "response_time": response_time,
                }
        except requests.exceptions.Timeout:
            self.services[service_name]["status"] = "timeout"
            return {
                "status": "timeout",
                "error": f"Request timed out after {timeout} seconds",
            }
        except Exception as e:
            self.services[service_name]["status"] = "error"
            return {
                "status": "error",
                "error": str(e),
            }

    def _check_smtp_service(self, service_name: str, service_config: Dict) -> Dict:
        host = service_config.get("host", "")
        port = service_config.get("port", 587)
        use_tls = service_config.get("use_tls", True)
        username = service_config.get("username", "")
        password = service_config.get("password", "")
        timeout = service_config.get("timeout", 10)
        if not host:
            self.services[service_name]["status"] = "error"
            return {
                "status": "error",
                "error": "Host not specified",
            }
        try:
            start_time = time.time()
            server = smtplib.SMTP(host, port, timeout=timeout)
            if use_tls:
                server.starttls()
            if username and password:
                server.login(username, password)
            server.quit()
            response_time = time.time() - start_time
            self.services[service_name]["status"] = "ok"
            return {
                "status": "ok",
                "response_time": response_time,
            }
        except smtplib.SMTPException as e:
            self.services[service_name]["status"] = "error"
            return {
                "status": "error",
                "error": str(e),
            }
        except Exception as e:
            self.services[service_name]["status"] = "error"
            return {
                "status": "error",
                "error": str(e),
            }

    def _check_database_service(self, service_name: str, service_config: Dict) -> Dict:
        # This method requires database drivers like mysql.connector, psycopg2, pymongo
        # Ensure they are in requirements.txt if used
        db_type = service_config.get("db_type", "").lower()
        host = service_config.get("host", "")
        port = service_config.get("port", 0)
        database = service_config.get("database", "")
        username = service_config.get("username", "")
        password = service_config.get("password", "")
        timeout = service_config.get("timeout", 10)

        if not all([db_type, host, port]):
            self.services[service_name]["status"] = "error"
            return {"status": "error", "error": "Incomplete database configuration"}
        
        try:
            start_time = time.time()
            # Example for PostgreSQL, add others as needed
            if db_type == "postgresql":
                import psycopg2
                conn = psycopg2.connect(host=host, port=port, dbname=database, user=username, password=password, connect_timeout=timeout)
                conn.close()
            # Add other DB types (MySQL, MongoDB) here if needed
            else:
                return {"status": "error", "error": f"Unsupported database type: {db_type}"}
            
            response_time = time.time() - start_time
            self.services[service_name]["status"] = "ok"
            return {"status": "ok", "response_time": response_time}
        except ImportError as ie:
            return {"status": "error", "error": f"{db_type} connector not installed: {ie}"}
        except Exception as e:
            self.services[service_name]["status"] = "error"
            return {"status": "error", "error": str(e)}

    def call_service(self, service_name: str, method: str, **kwargs) -> Dict:
        if service_name not in self.services:
            return {"status": "error", "error": f"Service not enabled: {service_name}"}
        service_config = self.services[service_name].get("config", {})
        service_type = service_config.get("type", "")
        if service_type == "http":
            if method == "request": return self._http_request(service_name, **kwargs)
        elif service_type == "smtp":
            if method == "send_email": return self._send_email(service_name, **kwargs)
        # Add other service types and methods
        return {"status": "error", "error": f"Unknown method or service type: {method} for {service_type}"}

    def _http_request(self, service_name: str, **kwargs) -> Dict:
        service_config = self.services[service_name].get("config", {})
        base_url = service_config.get("url", "")
        url = kwargs.get("url", "")
        method = kwargs.get("method", "GET")
        headers = {**service_config.get("headers", {}), **kwargs.get("headers", {})}
        params = kwargs.get("params", {})
        data = kwargs.get("data", None)
        json_data = kwargs.get("json", None)
        timeout = kwargs.get("timeout", service_config.get("timeout", 10))

        if base_url and url and not url.startswith(("http://", "https://")):
            url = base_url.rstrip("/") + "/" + url.lstrip("/")
        elif not url: url = base_url
        if not url: return {"status": "error", "error": "URL not specified"}

        try:
            response = self.session.request(method=method, url=url, headers=headers, params=params, data=data, json=json_data, timeout=timeout)
            try: response_data = response.json()
            except ValueError: response_data = response.text
            return {"status": "ok", "status_code": response.status_code, "headers": dict(response.headers), "data": response_data}
        except Exception as e: return {"status": "error", "error": str(e)}

    def _send_email(self, service_name: str, **kwargs) -> Dict:
        service_config = self.services[service_name].get("config", {})
        host = service_config.get("host", "")
        port = service_config.get("port", 587)
        use_tls = service_config.get("use_tls", True)
        username = service_config.get("username", "")
        password = service_config.get("password", "")
        sender = kwargs.get("sender", username)
        recipients = kwargs.get("recipients", [])
        subject = kwargs.get("subject", "")
        body = kwargs.get("body", "")
        html = kwargs.get("html", None)

        if not all([host, sender, recipients]):
            return {"status": "error", "error": "SMTP host, sender, or recipients not specified"}

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject; msg["From"] = sender; msg["To"] = ", ".join(recipients)
            msg.attach(MIMEText(body, "plain"))
            if html: msg.attach(MIMEText(html, "html"))
            server = smtplib.SMTP(host, port)
            if use_tls: server.starttls()
            if username and password: server.login(username, password)
            server.sendmail(sender, recipients, msg.as_string())
            server.quit()
            return {"status": "ok", "message": "Email sent successfully"}
        except Exception as e: return {"status": "error", "error": str(e)}
    
    def _database_query(self, service_name: str, **kwargs) -> Dict:
        # Placeholder - ensure full implementation from your original file
        logger.warning("_database_query not fully implemented in this snippet")
        return {"status": "error", "error": "_database_query not fully implemented"}

class NotificationSystem:
    """
    Handles notifications for the Telegram bot.
    """
    
    def __init__(self, bot_instance: Optional[TelegramBotInstance] = None, config_file_path: Optional[str] = None):
        """
        Initialize the notification system.
        
        Args:
            bot_instance: An instance of telegram.Bot for sending Telegram messages.
            config_file_path: Path to configuration file for notifications.
        """
        self.bot_instance = bot_instance
        self.config = {}
        self.channels = {}
        # ServiceIntegration might be used by some notification channels (e.g., email via a service)
        # If ServiceIntegration also needs a config, it should be passed when it's created.
        # For now, assuming default ServiceIntegration is okay or configured elsewhere if needed by a channel.
        self.service_integration = ServiceIntegration() 
        
        if config_file_path and os.path.exists(config_file_path):
            self.load_config(config_file_path)
        elif config_file_path: # If path provided but file doesn't exist
            logger.warning(f"Notification config file not found: {config_file_path}")
        
        logger.info("Notification system initialized")
    
    def load_config(self, config_file_path: str) -> bool:
        """
        Load notification configuration from a file.
        Args:
            config_file_path: Path to configuration file
        Returns:
            True if configuration was loaded successfully, False otherwise
        """
        try:
            with open(config_file_path, 'r') as f:
                self.config = json.load(f)
            
            for channel_name, channel_config in self.config.get("channels", {}).items():
                if channel_config.get("enabled", False):
                    self.channels[channel_name] = {
                        "config": channel_config,
                        "status": "initialized",
                    }
            logger.info(f"Loaded notification configuration from {config_file_path}")
            logger.info(f"Enabled channels: {', '.join(self.channels.keys())}")
            return True
        except Exception as e:
            logger.error(f"Error loading notification configuration: {e}")
            return False

    # ... (rest of NotificationSystem methods like save_config, register_channel, etc. remain largely the same) ...
    # Key change will be in _send_telegram_notification

    def save_config(self, config_file_path: str) -> bool:
        try:
            with open(config_file_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved notification configuration to {config_file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving notification configuration: {e}")
            return False

    def register_channel(self, channel_name: str, channel_config: Dict) -> bool:
        try:
            if "channels" not in self.config: self.config["channels"] = {}
            self.config["channels"][channel_name] = channel_config
            if channel_config.get("enabled", False):
                self.channels[channel_name] = {"config": channel_config, "status": "initialized"}
            logger.info(f"Registered notification channel: {channel_name}")
            return True
        except Exception as e:
            logger.error(f"Error registering channel: {e}"); return False

    def enable_channel(self, channel_name: str) -> bool:
        if channel_name not in self.config.get("channels", {}):
            logger.error(f"Notification channel not found: {channel_name}"); return False
        try:
            self.config["channels"][channel_name]["enabled"] = True
            self.channels[channel_name] = {"config": self.config["channels"][channel_name], "status": "initialized"}
            logger.info(f"Enabled notification channel: {channel_name}")
            return True
        except Exception as e:
            logger.error(f"Error enabling channel: {e}"); return False

    def disable_channel(self, channel_name: str) -> bool:
        if channel_name not in self.config.get("channels", {}):
            logger.error(f"Notification channel not found: {channel_name}"); return False
        try:
            self.config["channels"][channel_name]["enabled"] = False
            if channel_name in self.channels: del self.channels[channel_name]
            logger.info(f"Disabled notification channel: {channel_name}")
            return True
        except Exception as e:
            logger.error(f"Error disabling channel: {e}"); return False

    def send_notification(self, message: str, channel: str = None, **kwargs) -> Dict:
        if not message: return {"status": "error", "error": "Message not specified"}
        if channel:
            if channel not in self.channels: return {"status": "error", "error": f"Channel not enabled: {channel}"}
            return self._send_to_channel(channel, message, **kwargs)
        results = {}
        for channel_name in self.channels: results[channel_name] = self._send_to_channel(channel_name, message, **kwargs)
        success = any(result.get("status") == "ok" for result in results.values())
        return {"status": "ok" if success else "error", "results": results, "error": "Failed to send via any channel" if not success else None}

    def _send_to_channel(self, channel_name: str, message: str, **kwargs) -> Dict:
        channel_config = self.channels.get(channel_name, {}).get("config", {})
        channel_type = channel_config.get("type", "")
        if channel_type == "email": return self._send_email_notification(channel_config, message, **kwargs)
        elif channel_type == "telegram": return asyncio.run(self._send_telegram_notification(channel_config, message, **kwargs)) # MODIFIED to use asyncio.run for async method
        elif channel_type == "webhook": return self._send_webhook_notification(channel_config, message, **kwargs)
        elif channel_type == "sms": return self._send_sms_notification(channel_config, message, **kwargs)
        return {"status": "error", "error": f"Unknown channel type: {channel_type}"}

    def _send_email_notification(self, channel_config: Dict, message: str, **kwargs) -> Dict:
        # This method uses ServiceIntegration or direct SMTP, ensure it's complete from your original
        logger.warning("_send_email_notification might need review based on your full ServiceIntegration")
        # Assuming direct SMTP part from your code for now:
        host = channel_config.get("host", "")
        port = channel_config.get("port", 587)
        use_tls = channel_config.get("use_tls", True)
        username = channel_config.get("username", "")
        password = channel_config.get("password", "")
        sender = channel_config.get("sender", username)
        recipients = channel_config.get("recipients", [])
        subject = kwargs.get("subject", "Notification")
        html = kwargs.get("html", None)

        if not all([host, sender, recipients]):
            return {"status": "error", "error": "SMTP host, sender, or recipients not specified for email channel"}
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject; msg["From"] = sender; msg["To"] = ", ".join(recipients)
            msg.attach(MIMEText(message, "plain"))
            if html: msg.attach(MIMEText(html, "html"))
            server = smtplib.SMTP(host, port)
            if use_tls: server.starttls()
            if username and password: server.login(username, password)
            server.sendmail(sender, recipients, msg.as_string())
            server.quit()
            return {"status": "ok", "message": "Email notification sent successfully"}
        except Exception as e: return {"status": "error", "error": str(e)}

    async def _send_telegram_notification(self, channel_config: Dict, message: str, **kwargs) -> Dict:
        """
        Send a notification through Telegram using the provided bot_instance.
        """
        if not self.bot_instance:
            return {
                "status": "error",
                "error": "Telegram bot instance not provided to NotificationSystem",
            }

        chat_ids = channel_config.get("chat_ids", [])
        parse_mode = channel_config.get("parse_mode", "HTML") # Default to HTML as in your original
        
        if not chat_ids:
            return {
                "status": "error",
                "error": "Telegram chat IDs not specified in channel config",
            }
        
        results = {}
        for chat_id in chat_ids:
            try:
                # Use the bot_instance passed during __init__
                await self.bot_instance.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=parse_mode,
                )
                results[chat_id] = {"status": "ok"}
            except Exception as e:
                logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
                results[chat_id] = {"status": "error", "error": str(e)}
        
        success = any(result.get("status") == "ok" for result in results.values())
        if success:
            return {"status": "ok", "results": results}
        else:
            return {"status": "error", "error": "Failed to send Telegram notification to any chat", "results": results}

    def _send_webhook_notification(self, channel_config: Dict, message: str, **kwargs) -> Dict:
        # Ensure this is complete from your original
        url = channel_config.get("url", "")
        method = channel_config.get("method", "POST")
        headers = channel_config.get("headers", {})
        if not url: return {"status": "error", "error": "Webhook URL not specified"}
        try:
            payload = {"message": message, "timestamp": datetime.now().isoformat(), **kwargs}
            response = requests.request(method=method, url=url, headers=headers, json=payload)
            response.raise_for_status()
            return {"status": "ok", "status_code": response.status_code, "message": "Webhook sent"}
        except Exception as e: return {"status": "error", "error": str(e)}

    def _send_sms_notification(self, channel_config: Dict, message: str, **kwargs) -> Dict:
        # Placeholder - ensure full implementation from your original file
        # This requires SMS provider libraries like twilio or vonage in requirements.txt
        logger.warning("_send_sms_notification not fully implemented in this snippet")
        return {"status": "error", "error": "_send_sms_notification not fully implemented"}

# Ensure the main test function is also complete if you use it
def main():
    logger.info("Integration module main test function called.")
    # Example: Initialize NotificationSystem (assuming bot_instance would come from your main bot code)
    # For testing here, bot_instance can be None or a mock
    # notification_system = NotificationSystem(bot_instance=None, config_file_path="path_to_your_notification_config.json")
    # ... add test calls ...
    logger.info("Integration module test completed (partially, review full implementation).")

if __name__ == "__main__":
    main()

