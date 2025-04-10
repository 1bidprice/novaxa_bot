#!/usr/bin/env python3
"""
NOVAXA Deployment Test Script
This script tests the functionality of the deployed NOVAXA Telegram bot and web dashboard
"""

import os
import sys
import requests
import json
import logging
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("deployment_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("novaxa_test")

class NOVAXADeploymentTest:
    def __init__(self, bot_url, dashboard_url, bot_token=None):
        """Initialize the test with URLs and token"""
        self.bot_url = bot_url
        self.dashboard_url = dashboard_url
        self.bot_token = bot_token or os.getenv("BOT_TOKEN")
        
        logger.info("NOVAXA Deployment Test initialized")
        logger.info(f"Bot URL: {self.bot_url}")
        logger.info(f"Dashboard URL: {self.dashboard_url}")
        
        # Validate configuration
        if not self.bot_token:
            logger.warning("Bot token is missing. Some tests will be skipped.")
    
    def test_bot_health(self):
        """Test the health endpoint of the Telegram bot"""
        try:
            url = f"{self.bot_url}/health"
            logger.info(f"Testing bot health at {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Bot health check: PASSED")
                try:
                    data = response.json()
                    logger.info(f"Bot health response: {json.dumps(data, indent=2)}")
                except:
                    logger.info(f"Bot health response: {response.text}")
                return True
            else:
                logger.error(f"Bot health check FAILED with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Bot health check error: {str(e)}")
            return False
    
    def test_dashboard_health(self):
        """Test the health endpoint of the web dashboard"""
        try:
            url = f"{self.dashboard_url}/health"
            logger.info(f"Testing dashboard health at {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Dashboard health check: PASSED")
                try:
                    data = response.json()
                    logger.info(f"Dashboard health response: {json.dumps(data, indent=2)}")
                except:
                    logger.info(f"Dashboard health response: {response.text}")
                return True
            else:
                logger.error(f"Dashboard health check FAILED with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Dashboard health check error: {str(e)}")
            return False
    
    def test_bot_api_stocks(self):
        """Test the stocks API endpoint of the Telegram bot"""
        try:
            url = f"{self.bot_url}/api/stocks"
            logger.info(f"Testing bot stocks API at {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Bot stocks API check: PASSED")
                try:
                    data = response.json()
                    logger.info(f"Found {len(data.get('data', {}))} stocks")
                    return True
                except:
                    logger.error("Failed to parse JSON response")
                    return False
            else:
                logger.error(f"Bot stocks API check FAILED with status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Bot stocks API check error: {str(e)}")
            return False
    
    def test_bot_api_projects(self):
        """Test the projects API endpoint of the Telegram bot"""
        try:
            url = f"{self.bot_url}/api/projects"
            logger.info(f"Testing bot projects API at {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Bot projects API check: PASSED")
                try:
                    data = response.json()
                    logger.info(f"Found {len(data.get('data', {}))} projects")
                    return True
                except:
                    logger.error("Failed to parse JSON response")
                    return False
            else:
                logger.error(f"Bot projects API check FAILED with status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Bot projects API check error: {str(e)}")
            return False
    
    def test_dashboard_homepage(self):
        """Test the homepage of the web dashboard"""
        try:
            url = f"{self.dashboard_url}/"
            logger.info(f"Testing dashboard homepage at {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Dashboard homepage check: PASSED")
                if "NOVAXA Dashboard" in response.text:
                    logger.info("Dashboard title found in response")
                    return True
                else:
                    logger.warning("Dashboard title not found in response")
                    return False
            else:
                logger.error(f"Dashboard homepage check FAILED with status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Dashboard homepage check error: {str(e)}")
            return False
    
    def test_dashboard_api_proxy(self):
        """Test the API proxy endpoints of the web dashboard"""
        try:
            url = f"{self.dashboard_url}/api/proxy/stocks"
            logger.info(f"Testing dashboard API proxy at {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Dashboard API proxy check: PASSED")
                try:
                    data = response.json()
                    logger.info(f"API proxy response received")
                    return True
                except:
                    logger.error("Failed to parse JSON response")
                    return False
            else:
                logger.error(f"Dashboard API proxy check FAILED with status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Dashboard API proxy check error: {str(e)}")
            return False
    
    def test_telegram_bot_getme(self):
        """Test the Telegram Bot API getMe endpoint"""
        if not self.bot_token:
            logger.warning("Skipping Telegram Bot API test (no token provided)")
            return None
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            logger.info("Testing Telegram Bot API getMe")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_info = data.get("result", {})
                    logger.info(f"Telegram Bot API check: PASSED")
                    logger.info(f"Bot username: @{bot_info.get('username')}")
                    return True
                else:
                    logger.error(f"Telegram Bot API check FAILED: {data.get('description')}")
                    return False
            else:
                logger.error(f"Telegram Bot API check FAILED with status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Telegram Bot API check error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all deployment tests"""
        logger.info("Starting NOVAXA deployment tests")
        
        results = {
            "bot_health": self.test_bot_health(),
            "dashboard_health": self.test_dashboard_health(),
            "bot_api_stocks": self.test_bot_api_stocks(),
            "bot_api_projects": self.test_bot_api_projects(),
            "dashboard_homepage": self.test_dashboard_homepage(),
            "dashboard_api_proxy": self.test_dashboard_api_proxy(),
            "telegram_bot_api": self.test_telegram_bot_getme()
        }
        
        # Calculate success rate
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result is True)
        skipped_tests = sum(1 for result in results.values() if result is None)
        failed_tests = total_tests - passed_tests - skipped_tests
        
        success_rate = (passed_tests / (total_tests - skipped_tests)) * 100 if (total_tests - skipped_tests) > 0 else 0
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("NOVAXA DEPLOYMENT TEST SUMMARY")
        logger.info("="*50)
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Skipped: {skipped_tests}")
        logger.info(f"Success rate: {success_rate:.2f}%")
        logger.info("="*50)
        
        # Print detailed results
        logger.info("\nDetailed Results:")
        for test_name, result in results.items():
            status = "PASSED" if result is True else "FAILED" if result is False else "SKIPPED"
            logger.info(f"  {test_name}: {status}")
        
        return results

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="NOVAXA Deployment Test Script")
    parser.add_argument("--bot-url", default="https://novaxa-telegram-bot.onrender.com", help="URL of the Telegram bot service")
    parser.add_argument("--dashboard-url", default="https://novaxa-dashboard.onrender.com", help="URL of the web dashboard service")
    parser.add_argument("--token", help="Telegram bot token")
    
    args = parser.parse_args()
    
    # Start tests
    tester = NOVAXADeploymentTest(args.bot_url, args.dashboard_url, args.token)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
