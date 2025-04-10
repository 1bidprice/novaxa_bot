"""
Test script for NOVAXA website and Telegram bot functionality
"""

import requests
import json
import logging
import time
import os
import sys

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API base URL (change this to your actual API URL when deployed)
API_BASE_URL = "http://localhost:5000/api"

def test_api_endpoints():
    """Test all API endpoints"""
    logger.info("Testing API endpoints...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{API_BASE_URL.split('/api')[0]}")
        if response.status_code == 200:
            logger.info("✅ Root endpoint is working")
        else:
            logger.error(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Root endpoint error: {str(e)}")
    
    # Test stocks endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/stocks")
        if response.status_code == 200:
            stocks = response.json()
            if stocks and len(stocks) > 0:
                logger.info(f"✅ Stocks endpoint is working, returned {len(stocks)} stocks")
            else:
                logger.warning("⚠️ Stocks endpoint returned empty list")
        else:
            logger.error(f"❌ Stocks endpoint failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Stocks endpoint error: {str(e)}")
    
    # Test projects endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/projects")
        if response.status_code == 200:
            projects = response.json()
            if projects and len(projects) > 0:
                logger.info(f"✅ Projects endpoint is working, returned {len(projects)} projects")
            else:
                logger.warning("⚠️ Projects endpoint returned empty object")
        else:
            logger.error(f"❌ Projects endpoint failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Projects endpoint error: {str(e)}")
    
    # Test notifications endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/notifications")
        if response.status_code == 200:
            notifications = response.json()
            logger.info(f"✅ Notifications endpoint is working, returned {len(notifications)} notifications")
        else:
            logger.error(f"❌ Notifications endpoint failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Notifications endpoint error: {str(e)}")
    
    # Test alerts endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/alerts/check")
        if response.status_code == 200:
            alerts = response.json()
            logger.info(f"✅ Alerts endpoint is working, returned {len(alerts)} alerts")
        else:
            logger.error(f"❌ Alerts endpoint failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Alerts endpoint error: {str(e)}")

def test_specific_stock():
    """Test getting data for a specific stock"""
    logger.info("Testing specific stock data...")
    
    # Test OPAP.AT stock
    try:
        response = requests.get(f"{API_BASE_URL}/stocks/OPAP.AT")
        if response.status_code == 200:
            stock = response.json()
            if stock and "symbol" in stock and stock["symbol"] == "OPAP.AT":
                logger.info(f"✅ Stock OPAP.AT data: Price {stock['price']}€, Change {stock['change']:+.2f}€")
            else:
                logger.warning("⚠️ Stock OPAP.AT returned invalid data")
        else:
            logger.error(f"❌ Stock OPAP.AT request failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Stock OPAP.AT request error: {str(e)}")
    
    # Test MYTIL.AT stock
    try:
        response = requests.get(f"{API_BASE_URL}/stocks/MYTIL.AT")
        if response.status_code == 200:
            stock = response.json()
            if stock and "symbol" in stock and stock["symbol"] == "MYTIL.AT":
                logger.info(f"✅ Stock MYTIL.AT data: Price {stock['price']}€, Change {stock['change']:+.2f}€")
            else:
                logger.warning("⚠️ Stock MYTIL.AT returned invalid data")
        else:
            logger.error(f"❌ Stock MYTIL.AT request failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Stock MYTIL.AT request error: {str(e)}")

def test_specific_project():
    """Test getting data for a specific project"""
    logger.info("Testing specific project data...")
    
    # Test BidPrice project
    try:
        response = requests.get(f"{API_BASE_URL}/projects/bidprice")
        if response.status_code == 200:
            project = response.json()
            if project and "name" in project and project["name"] == "BidPrice":
                logger.info(f"✅ Project BidPrice data: Status {project['status']}, Progress {project['metrics']['progress']}%")
            else:
                logger.warning("⚠️ Project BidPrice returned invalid data")
        else:
            logger.error(f"❌ Project BidPrice request failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Project BidPrice request error: {str(e)}")
    
    # Test Amesis project
    try:
        response = requests.get(f"{API_BASE_URL}/projects/amesis")
        if response.status_code == 200:
            project = response.json()
            if project and "name" in project and project["name"] == "Amesis":
                logger.info(f"✅ Project Amesis data: Status {project['status']}, Progress {project['metrics']['progress']}%")
            else:
                logger.warning("⚠️ Project Amesis returned invalid data")
        else:
            logger.error(f"❌ Project Amesis request failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Project Amesis request error: {str(e)}")
    
    # Test Project6225 project
    try:
        response = requests.get(f"{API_BASE_URL}/projects/6225")
        if response.status_code == 200:
            project = response.json()
            if project and "name" in project and project["name"] == "Project6225":
                logger.info(f"✅ Project6225 data: Status {project['status']}, Progress {project['metrics']['progress']}%")
            else:
                logger.warning("⚠️ Project6225 returned invalid data")
        else:
            logger.error(f"❌ Project6225 request failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Project6225 request error: {str(e)}")

def test_web_api_proxy():
    """Test the web API proxy endpoints"""
    logger.info("Testing web API proxy endpoints...")
    
    # Test web API stocks endpoint
    try:
        response = requests.get("http://localhost:8080/web-api/stocks")
        if response.status_code == 200:
            stocks = response.json()
            if stocks and len(stocks) > 0:
                logger.info(f"✅ Web API stocks proxy is working, returned {len(stocks)} stocks")
            else:
                logger.warning("⚠️ Web API stocks proxy returned empty list")
        else:
            logger.error(f"❌ Web API stocks proxy failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Web API stocks proxy error: {str(e)}")
    
    # Test web API projects endpoint
    try:
        response = requests.get("http://localhost:8080/web-api/projects")
        if response.status_code == 200:
            projects = response.json()
            if projects and len(projects) > 0:
                logger.info(f"✅ Web API projects proxy is working, returned {len(projects)} projects")
            else:
                logger.warning("⚠️ Web API projects proxy returned empty object")
        else:
            logger.error(f"❌ Web API projects proxy failed: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Web API projects proxy error: {str(e)}")

def test_telegram_bot():
    """Test Telegram bot functionality"""
    logger.info("Testing Telegram bot functionality...")
    logger.info("Note: This is a manual test. Please check the following:")
    logger.info("1. Send /start to the bot and verify you receive a welcome message")
    logger.info("2. Send /stocks to the bot and verify you receive stock data")
    logger.info("3. Send /projects to the bot and verify you receive project data")
    logger.info("4. Test the inline keyboard buttons in the projects message")
    logger.info("5. Send /help to see all available commands")

def main():
    """Run all tests"""
    logger.info("Starting NOVAXA website and bot tests...")
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test specific stock data
    test_specific_stock()
    
    # Test specific project data
    test_specific_project()
    
    # Test web API proxy
    test_web_api_proxy()
    
    # Test Telegram bot
    test_telegram_bot()
    
    logger.info("All tests completed!")

if __name__ == "__main__":
    main()
