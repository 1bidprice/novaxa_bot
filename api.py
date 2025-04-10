"""
Backend API for NOVAXA Dashboard and Telegram Bot
Provides endpoints for stock data and project status
"""

from flask import Flask, jsonify, request
import logging
import json
import os
import requests
from datetime import datetime, timedelta
import threading
import schedule
import time

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='novaxa_api.log'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Stock data cache
stock_data_cache = {}

# Project data
projects = {
    "bidprice": {
        "name": "BidPrice",
        "status": "Active",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Πλατφόρμα δημοπρασιών προϊόντων",
        "logs": ["Σύστημα αρχικοποιήθηκε", "Όλες οι υπηρεσίες λειτουργούν"],
        "metrics": {
            "active_listings": 24,
            "new_bids": 12,
            "progress": 75
        }
    },
    "amesis": {
        "name": "Amesis",
        "status": "In Development",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Εφαρμογή αποστολής άμεσων pop-up μηνυμάτων",
        "logs": ["Ολοκληρώθηκε η μετάβαση της βάσης δεδομένων", "Ρυθμίστηκαν τα API endpoints"],
        "metrics": {
            "messages_sent": 156,
            "recipients": 42,
            "progress": 60
        }
    },
    "6225": {
        "name": "Project6225",
        "status": "Planning",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Πρόγραμμα e-commerce arbitrage + Print-on-Demand",
        "logs": ["Αρχική φάση σχεδιασμού", "Συλλογή απαιτήσεων"],
        "metrics": {
            "products": 18,
            "sales": 7,
            "progress": 30
        }
    }
}

# Notifications storage
notifications = []

# Default stocks to monitor
default_stocks = {
    "OPAP.AT": {"name": "ΟΠΑΠ", "threshold": 18.50},
    "MYTIL.AT": {"name": "METLEN", "threshold": 42.44}
}

# Stock monitoring class
class StockMonitor:
    def __init__(self):
        self.stock_data = {}
        self.default_stocks = default_stocks
        
    def get_stock_data(self, symbol):
        """Fetch current stock data from Yahoo Finance API"""
        try:
            # Check cache first
            if symbol in stock_data_cache and (datetime.now() - stock_data_cache[symbol]["timestamp"]).total_seconds() < 300:
                return stock_data_cache[symbol]["data"]
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                "region": "US",
                "lang": "en-US",
                "includePrePost": "false",
                "interval": "1d",
                "range": "1d",
                "corsDomain": "finance.yahoo.com",
                ".tsrc": "finance"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            
            # Check if we have valid data
            if "chart" in data and "result" in data["chart"] and data["chart"]["result"]:
                result = data["chart"]["result"][0]
                meta = result["meta"]
                
                # Get the latest price
                latest_price = meta.get("regularMarketPrice", 0)
                previous_close = meta.get("chartPreviousClose", 0)
                currency = meta.get("currency", "EUR")
                
                # Calculate change
                change = latest_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close else 0
                
                stock_info = {
                    "symbol": symbol,
                    "name": self.default_stocks.get(symbol, {}).get("name", symbol),
                    "price": latest_price,
                    "previous_close": previous_close,
                    "change": change,
                    "change_percent": change_percent,
                    "currency": currency,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                
                # Update stored data
                self.stock_data[symbol] = stock_info
                
                # Update cache
                stock_data_cache[symbol] = {
                    "data": stock_info,
                    "timestamp": datetime.now()
                }
                
                return stock_info
            else:
                logger.error(f"Invalid data format received for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
            return None
    
    def check_alerts(self, symbol=None):
        """
        Check if any stocks have crossed their alert thresholds
        Returns a list of alert messages
        """
        alerts = []
        symbols_to_check = [symbol] if symbol else self.default_stocks.keys()
        
        for sym in symbols_to_check:
            if sym not in self.default_stocks:
                continue
                
            threshold = self.default_stocks[sym].get("threshold")
            if not threshold:
                continue
                
            # Get fresh data
            stock_info = self.get_stock_data(sym)
            if not stock_info:
                continue
                
            current_price = stock_info["price"]
            stock_name = stock_info["name"]
            
            # Check if price crossed threshold (either above or below)
            if abs(current_price - threshold) / threshold <= 0.05:  # Within 5% of threshold
                direction = "πάνω από" if current_price >= threshold else "κάτω από"
                alert_msg = f"🚨 ΕΙΔΟΠΟΙΗΣΗ: Η μετοχή {stock_name} ({sym}) είναι {direction} το όριο των {threshold}€! Τρέχουσα τιμή: {current_price:.2f}€"
                
                # Add to notifications
                add_notification("stock", alert_msg)
                
                alerts.append(alert_msg)
                
        return alerts
    
    def get_stock_summary(self, symbol=None):
        """
        Generate a summary of stock data
        If symbol is provided, returns data for that stock only
        Otherwise returns data for all monitored stocks
        """
        if symbol:
            stock_info = self.get_stock_data(symbol)
            if stock_info:
                return stock_info
            return None
            
        # Get data for all stocks
        summary = []
        for sym in self.default_stocks.keys():
            stock_info = self.get_stock_data(sym)
            if stock_info:
                summary.append(stock_info)
                
        return summary

# Initialize stock monitor
stock_monitor = StockMonitor()

# Helper functions
def add_notification(notification_type, message):
    """Add a notification to the notifications list"""
    notification = {
        "id": len(notifications) + 1,
        "type": notification_type,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False
    }
    
    notifications.append(notification)
    logger.info(f"Added notification: {notification}")
    
    # Keep only the last 100 notifications
    if len(notifications) > 100:
        notifications.pop(0)

def update_project_metrics():
    """Update project metrics with simulated data"""
    # In a real implementation, this would fetch data from external sources
    
    # Update BidPrice metrics
    projects["bidprice"]["metrics"]["active_listings"] += 1 if datetime.now().minute % 2 == 0 else 0
    projects["bidprice"]["metrics"]["new_bids"] += 1 if datetime.now().minute % 3 == 0 else 0
    
    # Update Amesis metrics
    projects["amesis"]["metrics"]["messages_sent"] += 5 if datetime.now().minute % 5 == 0 else 0
    projects["amesis"]["metrics"]["recipients"] += 2 if datetime.now().minute % 7 == 0 else 0
    
    # Update Project6225 metrics
    projects["6225"]["metrics"]["products"] += 1 if datetime.now().minute % 11 == 0 else 0
    projects["6225"]["metrics"]["sales"] += 1 if datetime.now().minute % 13 == 0 else 0
    
    # Update last_update timestamp
    for project_id in projects:
        projects[project_id]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    logger.info("Project metrics updated")

# API routes
@app.route('/')
def index():
    """API root endpoint"""
    return jsonify({
        "name": "NOVAXA API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/stocks",
            "/api/stocks/<symbol>",
            "/api/projects",
            "/api/projects/<project_id>",
            "/api/notifications"
        ]
    })

@app.route('/api/stocks')
def get_stocks():
    """Get all stocks data"""
    stocks = stock_monitor.get_stock_summary()
    return jsonify(stocks)

@app.route('/api/stocks/<symbol>')
def get_stock(symbol):
    """Get data for a specific stock"""
    stock = stock_monitor.get_stock_summary(symbol)
    if stock:
        return jsonify(stock)
    return jsonify({"error": "Stock not found"}), 404

@app.route('/api/projects')
def get_projects():
    """Get all projects data"""
    return jsonify(projects)

@app.route('/api/projects/<project_id>')
def get_project(project_id):
    """Get data for a specific project"""
    if project_id in projects:
        return jsonify(projects[project_id])
    return jsonify({"error": "Project not found"}), 404

@app.route('/api/projects/<project_id>/logs')
def get_project_logs(project_id):
    """Get logs for a specific project"""
    if project_id in projects:
        return jsonify(projects[project_id]["logs"])
    return jsonify({"error": "Project not found"}), 404

@app.route('/api/notifications')
def get_notifications():
    """Get all notifications"""
    # Optional query parameter to filter by read status
    read_filter = request.args.get('read')
    
    if read_filter is not None:
        read_status = read_filter.lower() == 'true'
        filtered_notifications = [n for n in notifications if n["read"] == read_status]
        return jsonify(filtered_notifications)
    
    return jsonify(notifications)

@app.route('/api/notifications/<int:notification_id>', methods=['PUT'])
def update_notification(notification_id):
    """Update a notification (mark as read)"""
    for notification in notifications:
        if notification["id"] == notification_id:
            notification["read"] = True
            return jsonify(notification)
    
    return jsonify({"error": "Notification not found"}), 404

@app.route('/api/alerts/check')
def check_alerts():
    """Check for stock alerts"""
    alerts = stock_monitor.check_alerts()
    return jsonify(alerts)

# Scheduled tasks
def run_scheduled_tasks():
    """Run scheduled tasks in the background"""
    # Check stock alerts every 15 minutes
    schedule.every(15).minutes.do(stock_monitor.check_alerts)
    
    # Update project metrics every hour
    schedule.every(1).hours.do(update_project_metrics)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error in scheduler: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying

# Start the scheduler in a separate thread
def start_scheduler():
    scheduler_thread = threading.Thread(target=run_scheduled_tasks)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    logger.info("Scheduler started")

# Enable CORS for all routes
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    # Start the scheduler
    start_scheduler()
    
    # Start the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
