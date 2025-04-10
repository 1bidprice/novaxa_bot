"""
Enhanced NOVAXA Telegram Bot
A professional bot for stock alerts, project monitoring, and automated notifications
"""

import os
import logging
import time
import json
from datetime import datetime, timedelta
import threading
import schedule
import requests
from flask import Flask, request
import telebot
from telebot import types

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='novaxa_bot.log'
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"

# Initialize Flask app for webhook (if needed)
app = Flask(__name__)

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# Store user data
user_data = {}

# Project status tracking
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

# Stock monitoring
class StockMonitor:
    def __init__(self):
        self.stock_data = {}
        self.alert_thresholds = {}
        # Default Greek stocks as specified by the user
        self.default_stocks = {
            "OPAP.AT": {"name": "ΟΠΑΠ", "threshold": 18.50},
            "MYTIL.AT": {"name": "METLEN", "threshold": 42.44}
        }
        
    def add_stock(self, symbol, name, threshold=None):
        """Add a stock to monitor with optional price threshold for alerts"""
        self.default_stocks[symbol] = {"name": name, "threshold": threshold}
        logger.info(f"Added stock {name} ({symbol}) to monitoring list")
        
    def remove_stock(self, symbol):
        """Remove a stock from monitoring"""
        if symbol in self.default_stocks:
            stock_name = self.default_stocks[symbol]["name"]
            del self.default_stocks[symbol]
            logger.info(f"Removed stock {stock_name} ({symbol}) from monitoring list")
            return True
        return False
    
    def set_alert_threshold(self, symbol, threshold):
        """Set price threshold for alerts"""
        if symbol in self.default_stocks:
            self.default_stocks[symbol]["threshold"] = threshold
            logger.info(f"Set alert threshold for {symbol} to {threshold}")
            return True
        return False
    
    def get_stock_data(self, symbol):
        """Fetch current stock data from Yahoo Finance API"""
        try:
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
                alerts.append(alert_msg)
                
        return alerts
    
    def get_stock_summary(self, symbol=None):
        """
        Generate a summary of stock data
        If symbol is provided, returns data for that stock only
        Otherwise returns data for all monitored stocks
        """
        if symbol and symbol in self.default_stocks:
            stock_info = self.get_stock_data(symbol)
            if stock_info:
                return self._format_stock_message(stock_info)
            return f"Δεν βρέθηκαν δεδομένα για τη μετοχή {symbol}"
            
        # Get data for all stocks
        summary = "📊 *Σύνοψη Μετοχών* 📊\n\n"
        for sym in self.default_stocks.keys():
            stock_info = self.get_stock_data(sym)
            if stock_info:
                summary += self._format_stock_message(stock_info) + "\n\n"
                
        return summary.strip()
    
    def _format_stock_message(self, stock_info):
        """Format stock data as a readable message"""
        symbol = stock_info["symbol"]
        name = stock_info["name"]
        price = stock_info["price"]
        change = stock_info["change"]
        change_percent = stock_info["change_percent"]
        currency = stock_info["currency"]
        timestamp = stock_info["timestamp"]
        
        # Determine emoji based on price change
        emoji = "🔴" if change < 0 else "🟢" if change > 0 else "⚪️"
        
        message = f"{emoji} *{name}* ({symbol})\n"
        message += f"Τιμή: {price:.2f} {currency}\n"
        message += f"Μεταβολή: {change:+.2f} ({change_percent:+.2f}%)\n"
        message += f"Τελευταία ενημέρωση: {timestamp}"
        
        return message

# Initialize stock monitor
stock_monitor = StockMonitor()

# Command handlers
@bot.message_handler(commands=['start'])
def start_command(message):
    """Send welcome message when the command /start is issued."""
    user = message.from_user
    user_id = message.from_user.id
    
    # Store user data
    if user_id not in user_data:
        user_data[user_id] = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "chat_id": message.chat.id,
            "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    welcome_text = (
        f"Γεια σου {user.first_name}! Είμαι το NOVAXA bot.\n\n"
        f"Μπορώ να σε βοηθήσω με:\n"
        f"• Παρακολούθηση μετοχών και ειδοποιήσεις\n"
        f"• Διαχείριση των projects σου\n"
        f"• Αυτοματοποιημένες ειδοποιήσεις\n\n"
        f"Χρησιμοποίησε /help για να δεις όλες τις διαθέσιμες εντολές."
    )
    
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def help_command(message):
    """Send a message when the command /help is issued."""
    help_text = (
        "*Διαθέσιμες Εντολές:*\n\n"
        "*Γενικές Εντολές:*\n"
        "/start - Ξεκίνημα του bot\n"
        "/help - Εμφάνιση αυτού του μηνύματος βοήθειας\n"
        "/getid - Εμφάνιση του ID σου\n"
        "/status - Γενική κατάσταση συστήματος\n\n"
        
        "*Μετοχές:*\n"
        "/stocks - Εμφάνιση όλων των μετοχών\n"
        "/stock [σύμβολο] - Εμφάνιση συγκεκριμένης μετοχής\n"
        "/alert [σύμβολο] [τιμή] - Ορισμός ειδοποίησης για μετοχή\n\n"
        
        "*Projects:*\n"
        "/projects - Εμφάνιση όλων των projects\n"
        "/bidprice - Κατάσταση του BidPrice\n"
        "/amesis - Κατάσταση του Amesis\n"
        "/6225 - Κατάσταση του Project6225\n"
        "/logs [project] - Εμφάνιση logs για συγκεκριμένο project\n"
        "/progress - Καθημερινή αναφορά προόδου\n\n"
        
        "*Ειδοποιήσεις:*\n"
        "/broadcast [μήνυμα] - Αποστολή μαζικού μηνύματος\n"
        "/notify [μήνυμα] - Ορισμός ειδοποίησης\n"
        "/trending - Εμφάνιση τάσεων για Project6225\n"
        "/mystats - Εμφάνιση στατιστικών για όλα τα projects\n"
    )
    
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['getid'])
def getid_command(message):
    """Send user their Telegram ID."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    bot.reply_to(message, f"Το Telegram ID σου είναι: {user_id}\nΤο Chat ID είναι: {chat_id}")

@bot.message_handler(commands=['status'])
def status_command(message):
    """Send system status information."""
    uptime = get_uptime()
    
    status_text = (
        f"*Κατάσταση Συστήματος NOVAXA*\n\n"
        f"🟢 *Bot:* Λειτουργεί κανονικά\n"
        f"⏱ *Uptime:* {uptime}\n"
        f"📊 *Μετοχές:* {len(stock_monitor.default_stocks)} υπό παρακολούθηση\n"
        f"📋 *Projects:* {len(projects)} ενεργά\n"
        f"👥 *Χρήστες:* {len(user_data)} συνδεδεμένοι\n\n"
        f"Τελευταία ενημέρωση: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    bot.send_message(message.chat.id, status_text, parse_mode='Markdown')

# Stock related commands
@bot.message_handler(commands=['stocks'])
def stocks_command(message):
    """Display summary of all monitored stocks"""
    bot.send_message(message.chat.id, "Λαμβάνω δεδομένα μετοχών...")
    summary = stock_monitor.get_stock_summary()
    bot.send_message(message.chat.id, summary, parse_mode='Markdown')

@bot.message_handler(commands=['stock'])
def stock_command(message):
    """Display information for a specific stock"""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if not args:
        bot.reply_to(
            message,
            "Παρακαλώ δώστε το σύμβολο της μετοχής. Παράδειγμα: /stock OPAP.AT"
        )
        return
        
    symbol = args[0].upper()
    bot.send_message(message.chat.id, f"Λαμβάνω δεδομένα για τη μετοχή {symbol}...")
    
    stock_info = stock_monitor.get_stock_summary(symbol)
    bot.send_message(message.chat.id, stock_info, parse_mode='Markdown')

@bot.message_handler(commands=['alert'])
def alert_command(message):
    """Set price alert for a stock"""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if len(args) < 2:
        bot.reply_to(
            message,
            "Παρακαλώ δώστε το σύμβολο της μετοχής και την τιμή-στόχο. "
            "Παράδειγμα: /alert OPAP.AT 18.50"
        )
        return
        
    symbol = args[0].upper()
    try:
        threshold = float(args[1])
    except ValueError:
        bot.reply_to(message, "Η τιμή-στόχος πρέπει να είναι αριθμός.")
        return
        
    # Check if the stock exists in our monitor
    if symbol not in stock_monitor.default_stocks:
        # Try to add it
        stock_info = stock_monitor.get_stock_data(symbol)
        if not stock_info:
            bot.reply_to(
                message,
                f"Δεν βρέθηκε η μετοχή με σύμβολο {symbol}. "
                f"Βεβαιωθείτε ότι χρησιμοποιείτε το σωστό σύμβολο."
            )
            return
        stock_monitor.add_stock(symbol, stock_info["name"])
    
    # Set the alert threshold
    success = stock_monitor.set_alert_threshold(symbol, threshold)
    if success:
        bot.reply_to(
            message,
            f"Η ειδοποίηση για τη μετοχή {symbol} ορίστηκε στα {threshold}€."
        )
    else:
        bot.reply_to(
            message,
            f"Σφάλμα κατά τον ορισμό της ειδοποίησης για τη μετοχή {symbol}."
        )

# Project related commands
@bot.message_handler(commands=['projects'])
def projects_command(message):
    """Display summary of all projects"""
    message_text = "📋 *Κατάσταση Projects* 📋\n\n"
    
    for project_id, project_data in projects.items():
        status_emoji = "🟢" if project_data["status"] == "Active" else "🟡" if project_data["status"] == "In Development" else "🔵"
        message_text += f"{status_emoji} *{project_data['name']}*\n"
        message_text += f"Κατάσταση: {project_data['status']}\n"
        message_text += f"Τελευταία ενημέρωση: {project_data['last_update']}\n"
        message_text += f"Περιγραφή: {project_data['description']}\n"
        message_text += f"Πρόοδος: {project_data['metrics']['progress']}%\n\n"
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_bidprice = types.InlineKeyboardButton("BidPrice", callback_data="project_bidprice")
    btn_amesis = types.InlineKeyboardButton("Amesis", callback_data="project_amesis")
    btn_6225 = types.InlineKeyboardButton("Project6225", callback_data="project_6225")
    markup.add(btn_bidprice, btn_amesis, btn_6225)
    
    bot.send_message(message.chat.id, message_text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['bidprice'])
def bidprice_command(message):
    """Display BidPrice project status"""
    send_project_status(message, "bidprice")

@bot.message_handler(commands=['amesis'])
def amesis_command(message):
    """Display Amesis project status"""
    send_project_status(message, "amesis")

@bot.message_handler(commands=['6225'])
def project6225_command(message):
    """Display Project6225 status"""
    send_project_status(message, "6225")

def send_project_status(message, project_id):
    """Helper function to send project status"""
    if project_id not in projects:
        bot.reply_to(message, f"Το project {project_id} δεν βρέθηκε.")
        return
        
    project_data = projects[project_id]
    metrics = project_data["metrics"]
    
    message_text = f"📊 *{project_data['name']}* 📊\n\n"
    message_text += f"*Κατάσταση:* {project_data['status']}\n"
    message_text += f"*Τελευταία ενημέρωση:* {project_data['last_update']}\n"
    message_text += f"*Περιγραφή:* {project_data['description']}\n\n"
    
    # Add project-specific metrics
    message_text += "*Μετρήσεις:*\n"
    if project_id == "bidprice":
        message_text += f"• Ενεργές αγγελίες: {metrics['active_listings']}\n"
        message_text += f"• Νέες προσφορές: {metrics['new_bids']}\n"
    elif project_id == "amesis":
        message_text += f"• Μηνύματα που στάλθηκαν: {metrics['messages_sent']}\n"
        message_text += f"• Παραλήπτες: {metrics['recipients']}\n"
    elif project_id == "6225":
        message_text += f"• Προϊόντα: {metrics['products']}\n"
        message_text += f"• Πωλήσεις: {metrics['sales']}\n"
    
    message_text += f"• Πρόοδος: {metrics['progress']}%\n\n"
    
    message_text += f"*Τελευταία logs:*\n"
    # Add the last 3 logs
    for log in project_data['logs'][-3:]:
        message_text += f"• {log}\n"
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_logs = types.InlineKeyboardButton("Πλήρη Logs", callback_data=f"logs_{project_id}")
    btn_back = types.InlineKeyboardButton("Επιστροφή στα Projects", callback_data="back_to_projects")
    markup.add(btn_logs, btn_back)
    
    bot.send_message(message.chat.id, message_text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['logs'])
def logs_command(message):
    """Display logs for a specific project"""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if not args:
        bot.reply_to(
            message,
            "Παρακαλώ δώστε το όνομα του project. Παράδειγμα: /logs bidprice"
        )
        return
        
    project_id = args[0].lower()
    if project_id in projects:
        send_project_logs(message, project_id)
    else:
        bot.reply_to(
            message,
            f"Το project {project_id} δεν βρέθηκε. Διαθέσιμα projects: bidprice, amesis, 6225"
        )

def send_project_logs(message, project_id):
    """Helper function to send project logs"""
    project_data = projects[project_id]
    
    message_text = f"📝 *Logs για {project_data['name']}* 📝\n\n"
    
    # Add all logs
    for i, log in enumerate(project_data['logs'], 1):
        message_text += f"{i}. {log}\n"
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_back_project = types.InlineKeyboardButton(f"Επιστροφή στο {project_data['name']}", callback_data=f"project_{project_id}")
    btn_back_projects = types.InlineKeyboardButton("Επιστροφή στα Projects", callback_data="back_to_projects")
    markup.add(btn_back_project, btn_back_projects)
    
    bot.send_message(message.chat.id, message_text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['progress'])
def progress_command(message):
    """Display daily progress report for all projects"""
    message_text = "📈 *Καθημερινή Αναφορά Προόδου* 📈\n\n"
    message_text += f"*Ημερομηνία:* {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    # Add stock summary
    message_text += "*Μετοχές:*\n"
    for symbol, stock_data in stock_monitor.default_stocks.items():
        stock_info = stock_monitor.get_stock_data(symbol)
        if stock_info:
            change_emoji = "🔴" if stock_info["change"] < 0 else "🟢" if stock_info["change"] > 0 else "⚪️"
            message_text += f"{change_emoji} {stock_data['name']}: {stock_info['price']:.2f}€ ({stock_info['change']:+.2f}€)\n"
    
    message_text += "\n*Projects:*\n"
    
    # Add project progress
    for project_id, project_data in projects.items():
        status_emoji = "🟢" if project_data["status"] == "Active" else "🟡" if project_data["status"] == "In Development" else "🔵"
        message_text += f"{status_emoji} *{project_data['name']}*\n"
        message_text += f"  Πρόοδος: {project_data['metrics']['progress']}%\n"
        
        # Add project-specific metrics
        if project_id == "bidprice":
            message_text += f"  Ενεργές αγγελίες: {project_data['metrics']['active_listings']}\n"
            message_text += f"  Νέες προσφορές: {project_data['metrics']['new_bids']}\n"
        elif project_id == "amesis":
            message_text += f"  Μηνύματα: {project_data['metrics']['messages_sent']}\n"
            message_text += f"  Παραλήπτες: {project_data['metrics']['recipients']}\n"
        elif project_id == "6225":
            message_text += f"  Προϊόντα: {project_data['metrics']['products']}\n"
            message_text += f"  Πωλήσεις: {project_data['metrics']['sales']}\n"
        
        message_text += f"  Τελευταία ενέργεια: {project_data['logs'][-1]}\n\n"
    
    bot.send_message(message.chat.id, message_text, parse_mode='Markdown')

@bot.message_handler(commands=['trending'])
def trending_command(message):
    """Display trending products for Project6225"""
    trending_products = [
        {"name": "Custom T-Shirt Design #1", "sales": 12, "growth": "+25%"},
        {"name": "Phone Case Model X", "sales": 8, "growth": "+15%"},
        {"name": "Personalized Mug", "sales": 6, "growth": "+10%"}
    ]
    
    message_text = "📊 *Trending Products - Project6225* 📊\n\n"
    
    for i, product in enumerate(trending_products, 1):
        message_text += f"{i}. *{product['name']}*\n"
        message_text += f"   Πωλήσεις: {product['sales']}\n"
        message_text += f"   Ανάπτυξη: {product['growth']}\n\n"
    
    message_text += "*Προτεινόμενες Ενέργειες:*\n"
    message_text += "• Αύξηση διαφημιστικού προϋπολογισμού για το #1\n"
    message_text += "• Δημιουργία παρόμοιων προϊόντων με το #2\n"
    message_text += "• Προσφορά έκπτωσης για το #3\n"
    
    bot.send_message(message.chat.id, message_text, parse_mode='Markdown')

@bot.message_handler(commands=['mystats'])
def mystats_command(message):
    """Display statistics for all projects"""
    message_text = "📊 *Στατιστικά Projects* 📊\n\n"
    
    # BidPrice stats
    message_text += "*BidPrice:*\n"
    message_text += f"• Ενεργές αγγελίες: {projects['bidprice']['metrics']['active_listings']}\n"
    message_text += f"• Νέες προσφορές: {projects['bidprice']['metrics']['new_bids']}\n"
    message_text += f"• Ποσοστό ολοκλήρωσης: {projects['bidprice']['metrics']['progress']}%\n\n"
    
    # Amesis stats
    message_text += "*Amesis:*\n"
    message_text += f"• Μηνύματα που στάλθηκαν: {projects['amesis']['metrics']['messages_sent']}\n"
    message_text += f"• Παραλήπτες: {projects['amesis']['metrics']['recipients']}\n"
    message_text += f"• Ποσοστό ολοκλήρωσης: {projects['amesis']['metrics']['progress']}%\n\n"
    
    # Project6225 stats
    message_text += "*Project6225:*\n"
    message_text += f"• Προϊόντα: {projects['6225']['metrics']['products']}\n"
    message_text += f"• Πωλήσεις: {projects['6225']['metrics']['sales']}\n"
    message_text += f"• Ποσοστό ολοκλήρωσης: {projects['6225']['metrics']['progress']}%\n\n"
    
    message_text += "*Συνολική Πρόοδος:* 55%"
    
    bot.send_message(message.chat.id, message_text, parse_mode='Markdown')

# Notification commands
@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    """Send a broadcast message to all users (admin only)"""
    user_id = message.from_user.id
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    # In a real implementation, you would check if the user is an admin
    # For now, we'll assume the user is authorized
    
    if not args:
        bot.reply_to(
            message,
            "Παρακαλώ δώστε το μήνυμα που θέλετε να στείλετε. "
            "Παράδειγμα: /broadcast Σημαντική ενημέρωση!"
        )
        return
        
    broadcast_text = " ".join(args)
    
    # For now, just echo back the message
    bot.reply_to(
        message,
        f"📣 *Broadcast Message*\n\n{broadcast_text}\n\n"
        f"Σε κανονική λειτουργία, αυτό το μήνυμα θα στελνόταν σε όλους τους χρήστες.",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['notify'])
def notify_command(message):
    """Set a notification"""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if not args:
        bot.reply_to(
            message,
            "Παρακαλώ δώστε το μήνυμα ειδοποίησης. "
            "Παράδειγμα: /notify Υπενθύμιση για τη συνάντηση"
        )
        return
        
    notification_text = " ".join(args)
    
    # In a real implementation, you would store the notification
    # For now, just echo back the message
    bot.reply_to(
        message,
        f"🔔 *Ειδοποίηση Ρυθμίστηκε*\n\n"
        f"{notification_text}\n\n"
        f"Θα λάβετε αυτή την ειδοποίηση στο μέλλον.",
        parse_mode='Markdown'
    )

# Callback query handler
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Handle callback queries from inline keyboards"""
    if call.data.startswith("project_"):
        project_id = call.data.split("_")[1]
        send_project_status_callback(call, project_id)
    elif call.data.startswith("logs_"):
        project_id = call.data.split("_")[1]
        send_project_logs_callback(call, project_id)
    elif call.data == "back_to_projects":
        send_projects_callback(call)

def send_project_status_callback(call, project_id):
    """Send project status for callback queries"""
    if project_id not in projects:
        bot.answer_callback_query(call.id, text=f"Το project {project_id} δεν βρέθηκε.")
        return
        
    project_data = projects[project_id]
    metrics = project_data["metrics"]
    
    message_text = f"📊 *{project_data['name']}* 📊\n\n"
    message_text += f"*Κατάσταση:* {project_data['status']}\n"
    message_text += f"*Τελευταία ενημέρωση:* {project_data['last_update']}\n"
    message_text += f"*Περιγραφή:* {project_data['description']}\n\n"
    
    # Add project-specific metrics
    message_text += "*Μετρήσεις:*\n"
    if project_id == "bidprice":
        message_text += f"• Ενεργές αγγελίες: {metrics['active_listings']}\n"
        message_text += f"• Νέες προσφορές: {metrics['new_bids']}\n"
    elif project_id == "amesis":
        message_text += f"• Μηνύματα που στάλθηκαν: {metrics['messages_sent']}\n"
        message_text += f"• Παραλήπτες: {metrics['recipients']}\n"
    elif project_id == "6225":
        message_text += f"• Προϊόντα: {metrics['products']}\n"
        message_text += f"• Πωλήσεις: {metrics['sales']}\n"
    
    message_text += f"• Πρόοδος: {metrics['progress']}%\n\n"
    
    message_text += f"*Τελευταία logs:*\n"
    # Add the last 3 logs
    for log in project_data['logs'][-3:]:
        message_text += f"• {log}\n"
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_logs = types.InlineKeyboardButton("Πλήρη Logs", callback_data=f"logs_{project_id}")
    btn_back = types.InlineKeyboardButton("Επιστροφή στα Projects", callback_data="back_to_projects")
    markup.add(btn_logs, btn_back)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=message_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    
    bot.answer_callback_query(call.id)

def send_project_logs_callback(call, project_id):
    """Send project logs for callback queries"""
    project_data = projects[project_id]
    
    message_text = f"📝 *Logs για {project_data['name']}* 📝\n\n"
    
    # Add all logs
    for i, log in enumerate(project_data['logs'], 1):
        message_text += f"{i}. {log}\n"
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_back_project = types.InlineKeyboardButton(f"Επιστροφή στο {project_data['name']}", callback_data=f"project_{project_id}")
    btn_back_projects = types.InlineKeyboardButton("Επιστροφή στα Projects", callback_data="back_to_projects")
    markup.add(btn_back_project, btn_back_projects)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=message_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    
    bot.answer_callback_query(call.id)

def send_projects_callback(call):
    """Send projects overview for callback queries"""
    message_text = "📋 *Κατάσταση Projects* 📋\n\n"
    
    for project_id, project_data in projects.items():
        status_emoji = "🟢" if project_data["status"] == "Active" else "🟡" if project_data["status"] == "In Development" else "🔵"
        message_text += f"{status_emoji} *{project_data['name']}*\n"
        message_text += f"Κατάσταση: {project_data['status']}\n"
        message_text += f"Τελευταία ενημέρωση: {project_data['last_update']}\n"
        message_text += f"Περιγραφή: {project_data['description']}\n"
        message_text += f"Πρόοδος: {project_data['metrics']['progress']}%\n\n"
    
    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_bidprice = types.InlineKeyboardButton("BidPrice", callback_data="project_bidprice")
    btn_amesis = types.InlineKeyboardButton("Amesis", callback_data="project_amesis")
    btn_6225 = types.InlineKeyboardButton("Project6225", callback_data="project_6225")
    markup.add(btn_bidprice, btn_amesis, btn_6225)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=message_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    
    bot.answer_callback_query(call.id)

# Helper functions
def get_uptime():
    """Get system uptime"""
    # In a real implementation, you would get the actual uptime
    # For now, return a placeholder
    return "3 ημέρες, 7 ώρες, 22 λεπτά"

# Scheduled tasks
def check_stock_alerts():
    """Check for stock alerts and send notifications"""
    alerts = stock_monitor.check_alerts()
    if alerts:
        # In a real implementation, you would send these alerts to the user
        for alert in alerts:
            logger.info(f"Stock alert: {alert}")
            # Send to all users
            for user_id, data in user_data.items():
                try:
                    bot.send_message(data["chat_id"], alert, parse_mode='Markdown')
                except Exception as e:
                    logger.error(f"Error sending alert to user {user_id}: {str(e)}")

def update_project_data():
    """Update project data with new information"""
    # In a real implementation, you would fetch data from external sources
    # For now, just update the last_update field
    for project_id in projects:
        projects[project_id]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    logger.info("Project data updated")

def send_daily_report():
    """Send daily progress report to all users"""
    # In a real implementation, you would generate a comprehensive report
    # For now, just log that the report would be sent
    logger.info("Daily report would be sent to all users")
    
    # Send to all users
    for user_id, data in user_data.items():
        try:
            # Create a message for the daily report
            message_text = "📈 *Καθημερινή Αναφορά Προόδου* 📈\n\n"
            message_text += f"*Ημερομηνία:* {datetime.now().strftime('%Y-%m-%d')}\n\n"
            
            # Add stock summary
            message_text += "*Μετοχές:*\n"
            for symbol, stock_data in stock_monitor.default_stocks.items():
                stock_info = stock_monitor.get_stock_data(symbol)
                if stock_info:
                    change_emoji = "🔴" if stock_info["change"] < 0 else "🟢" if stock_info["change"] > 0 else "⚪️"
                    message_text += f"{change_emoji} {stock_data['name']}: {stock_info['price']:.2f}€ ({stock_info['change']:+.2f}€)\n"
            
            message_text += "\n*Projects:*\n"
            
            # Add project progress
            for project_id, project_data in projects.items():
                status_emoji = "🟢" if project_data["status"] == "Active" else "🟡" if project_data["status"] == "In Development" else "🔵"
                message_text += f"{status_emoji} *{project_data['name']}*\n"
                message_text += f"  Πρόοδος: {project_data['metrics']['progress']}%\n"
                
                # Add project-specific metrics
                if project_id == "bidprice":
                    message_text += f"  Ενεργές αγγελίες: {project_data['metrics']['active_listings']}\n"
                    message_text += f"  Νέες προσφορές: {project_data['metrics']['new_bids']}\n"
                elif project_id == "amesis":
                    message_text += f"  Μηνύματα: {project_data['metrics']['messages_sent']}\n"
                    message_text += f"  Παραλήπτες: {project_data['metrics']['recipients']}\n"
                elif project_id == "6225":
                    message_text += f"  Προϊόντα: {project_data['metrics']['products']}\n"
                    message_text += f"  Πωλήσεις: {project_data['metrics']['sales']}\n"
                
                message_text += f"  Τελευταία ενέργεια: {project_data['logs'][-1]}\n\n"
            
            bot.send_message(data["chat_id"], message_text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error sending daily report to user {user_id}: {str(e)}")

# Background scheduler
def run_scheduler():
    """Run the scheduler in the background"""
    # Check stock alerts every 15 minutes
    schedule.every(15).minutes.do(check_stock_alerts)
    
    # Update project data every hour
    schedule.every(1).hours.do(update_project_data)
    
    # Send daily report at 9:00 AM
    schedule.every().day.at("09:00").do(send_daily_report)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error in scheduler: {str(e)}")
            time.sleep(60)  # Wait a minute before retrying

# Flask route for webhook (if needed)
@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle webhook requests from Telegram"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    else:
        return 'error', 403

@app.route('/')
def index():
    """Simple index page to check if the server is running"""
    return 'NOVAXA Bot is running!'

def main():
    """Start the bot."""
    # Remove webhook if exists
    bot.remove_webhook()
    
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    try:
        # Start polling
        logger.info("Starting bot polling...")
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        logger.error(f"Error in main polling loop: {str(e)}")

if __name__ == '__main__':
    # Choose between polling and webhook based on environment
    if os.environ.get('WEBHOOK_URL'):
        # Set webhook
        webhook_url = os.environ.get('WEBHOOK_URL')
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        
        # Start Flask server
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        # Start polling
        main()
