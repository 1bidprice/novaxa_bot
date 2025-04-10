"""
Integration module for NOVAXA website and Telegram bot
Connects the backend API with the Telegram bot functionality
"""

import os
import logging
import requests
import json
from flask import Flask, request, jsonify, render_template
import telebot
from telebot import types
import threading
import time

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='novaxa_integration.log'
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = "7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM"

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# API base URL (change this to your actual API URL when deployed)
API_BASE_URL = "http://localhost:5000/api"

# Store user data
user_data = {}

# Helper functions
def get_stock_data():
    """Get stock data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/stocks")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get stock data: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error getting stock data: {str(e)}")
        return []

def get_project_data(project_id=None):
    """Get project data from API"""
    try:
        if project_id:
            response = requests.get(f"{API_BASE_URL}/projects/{project_id}")
        else:
            response = requests.get(f"{API_BASE_URL}/projects")
            
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get project data: {response.status_code}")
            return {} if project_id else {}
    except Exception as e:
        logger.error(f"Error getting project data: {str(e)}")
        return {} if project_id else {}

def get_notifications(read=None):
    """Get notifications from API"""
    try:
        url = f"{API_BASE_URL}/notifications"
        if read is not None:
            url += f"?read={'true' if read else 'false'}"
            
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get notifications: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        return []

def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        response = requests.put(f"{API_BASE_URL}/notifications/{notification_id}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return False

def check_stock_alerts():
    """Check for stock alerts"""
    try:
        response = requests.get(f"{API_BASE_URL}/alerts/check")
        if response.status_code == 200:
            alerts = response.json()
            if alerts:
                # Send alerts to all users
                for user_id, data in user_data.items():
                    for alert in alerts:
                        try:
                            bot.send_message(data["chat_id"], alert, parse_mode='Markdown')
                        except Exception as e:
                            logger.error(f"Error sending alert to user {user_id}: {str(e)}")
            return alerts
        else:
            logger.error(f"Failed to check stock alerts: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error checking stock alerts: {str(e)}")
        return []

# Web routes
@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/stocks')
def stocks_page():
    """Render the stocks page"""
    return render_template('stocks.html')

@app.route('/projects')
def projects_page():
    """Render the projects page"""
    return render_template('projects.html')

@app.route('/notifications')
def notifications_page():
    """Render the notifications page"""
    return render_template('notifications.html')

@app.route('/settings')
def settings_page():
    """Render the settings page"""
    return render_template('settings.html')

# API proxy routes (to avoid CORS issues)
@app.route('/web-api/stocks')
def web_api_stocks():
    """Proxy for stocks API"""
    stocks = get_stock_data()
    return jsonify(stocks)

@app.route('/web-api/stocks/<symbol>')
def web_api_stock(symbol):
    """Proxy for specific stock API"""
    try:
        response = requests.get(f"{API_BASE_URL}/stocks/{symbol}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error in web API stock proxy: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/web-api/projects')
def web_api_projects():
    """Proxy for projects API"""
    projects = get_project_data()
    return jsonify(projects)

@app.route('/web-api/projects/<project_id>')
def web_api_project(project_id):
    """Proxy for specific project API"""
    project = get_project_data(project_id)
    return jsonify(project)

@app.route('/web-api/notifications')
def web_api_notifications():
    """Proxy for notifications API"""
    read = request.args.get('read')
    if read is not None:
        read_status = read.lower() == 'true'
        notifications = get_notifications(read_status)
    else:
        notifications = get_notifications()
    return jsonify(notifications)

@app.route('/web-api/notifications/<int:notification_id>', methods=['PUT'])
def web_api_mark_notification_read(notification_id):
    """Proxy for marking notification as read"""
    success = mark_notification_read(notification_id)
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Failed to mark notification as read"}), 500

@app.route('/web-api/alerts/check')
def web_api_check_alerts():
    """Proxy for checking stock alerts"""
    alerts = check_stock_alerts()
    return jsonify(alerts)

# Telegram bot webhook route
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

# Bot command handlers
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
            "joined_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    welcome_text = (
        f"Γεια σου {user.first_name}! Είμαι το NOVAXA bot.\n\n"
        f"Μπορώ να σε βοηθήσω με:\n"
        f"• Παρακολούθηση μετοχών και ειδοποιήσεις\n"
        f"• Διαχείριση των projects σου\n"
        f"• Αυτοματοποιημένες ειδοποιήσεις\n\n"
        f"Χρησιμοποίησε /help για να δεις όλες τις διαθέσιμες εντολές.\n\n"
        f"Επίσης, μπορείς να επισκεφθείς το dashboard στο: https://novaxa-dashboard.example.com"
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
        "/mystats - Εμφάνιση στατιστικών για όλα τα projects\n\n"
        
        "*Web Dashboard:*\n"
        "Επισκέψου το dashboard στο: https://novaxa-dashboard.example.com"
    )
    
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['stocks'])
def stocks_command(message):
    """Display summary of all monitored stocks"""
    bot.send_message(message.chat.id, "Λαμβάνω δεδομένα μετοχών...")
    
    stocks = get_stock_data()
    if not stocks:
        bot.send_message(message.chat.id, "Δεν ήταν δυνατή η λήψη δεδομένων μετοχών. Παρακαλώ δοκιμάστε αργότερα.")
        return
    
    # Format stock data
    summary = "📊 *Σύνοψη Μετοχών* 📊\n\n"
    for stock in stocks:
        # Determine emoji based on price change
        emoji = "🔴" if stock["change"] < 0 else "🟢" if stock["change"] > 0 else "⚪️"
        
        summary += f"{emoji} *{stock['name']}* ({stock['symbol']})\n"
        summary += f"Τιμή: {stock['price']:.2f} {stock['currency']}\n"
        summary += f"Μεταβολή: {stock['change']:+.2f} ({stock['change_percent']:+.2f}%)\n"
        summary += f"Τελευταία ενημέρωση: {stock['timestamp']}\n\n"
    
    bot.send_message(message.chat.id, summary, parse_mode='Markdown')

@bot.message_handler(commands=['projects'])
def projects_command(message):
    """Display summary of all projects"""
    projects_data = get_project_data()
    if not projects_data:
        bot.send_message(message.chat.id, "Δεν ήταν δυνατή η λήψη δεδομένων projects. Παρακαλώ δοκιμάστε αργότερα.")
        return
    
    message_text = "📋 *Κατάσταση Projects* 📋\n\n"
    
    for project_id, project_data in projects_data.items():
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
    project_data = get_project_data(project_id)
    if not project_data:
        bot.answer_callback_query(call.id, text=f"Το project {project_id} δεν βρέθηκε.")
        return
    
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
    btn_dashboard = types.InlineKeyboardButton("Προβολή στο Dashboard", url="https://novaxa-dashboard.example.com/projects")
    markup.add(btn_logs, btn_back, btn_dashboard)
    
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
    project_data = get_project_data(project_id)
    if not project_data:
        bot.answer_callback_query(call.id, text=f"Το project {project_id} δεν βρέθηκε.")
        return
    
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
    projects_data = get_project_data()
    if not projects_data:
        bot.answer_callback_query(call.id, text="Δεν ήταν δυνατή η λήψη δεδομένων projects.")
        return
    
    message_text = "📋 *Κατάσταση Projects* 📋\n\n"
    
    for project_id, project_data in projects_data.items():
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
    btn_dashboard = types.InlineKeyboardButton("Προβολή στο Dashboard", url="https://novaxa-dashboard.example.com/projects")
    markup.add(btn_bidprice, btn_amesis, btn_6225)
    markup.add(btn_dashboard)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=message_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    
    bot.answer_callback_query(call.id)

# Start the bot in a separate thread
def start_bot():
    """Start the bot polling in a separate thread"""
    try:
        logger.info("Starting bot polling...")
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        logger.error(f"Error in bot polling: {str(e)}")

if __name__ == '__main__':
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start the Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
