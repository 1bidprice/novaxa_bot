#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Telegram Bot & Dashboard with CRM and Smart Reply
"""

import os
import sys
import logging
import json
import time
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable

# Third-party imports for Bot
import telegram
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

# Third-party imports for Flask Dashboard
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.serving import run_simple # For running Flask in a thread

# --- Load environment variables from .env file ---
from dotenv import load_dotenv
load_dotenv() # Load variables from .env file into environment

# --- Import CRM and Smart Reply Modules ---
module_base_path = "/home/ubuntu/workspace/novaxa_bot"
if module_base_path not in sys.path:
    sys.path.insert(0, module_base_path)

try:
    from crm.crm_module import CRMModule
    from smart_reply.smart_reply_engine import SmartReplyEngine
    CRM_ENABLED = True
    SMART_REPLY_ENABLED = True
    logging.info("Successfully imported CRMModule and SmartReplyEngine.")
except ImportError as e:
    CRMModule = None
    SmartReplyEngine = None
    CRM_ENABLED = False
    SMART_REPLY_ENABLED = False
    logging.error(f"Failed to import CRM or Smart Reply modules: {e}. CRM and Smart Reply features will be disabled.")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Flask App Definition (Global) ---
app = Flask(__name__, template_folder="/home/ubuntu/workspace/novaxa_bot/templates", static_folder="/home/ubuntu/workspace/novaxa_bot/static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super_secret_key_for_dev")

# Environment variables for dashboard credentials
DASHBOARD_USERNAME = os.environ.get("DASHBOARD_USERNAME", "admin")
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "password")

# Global bot instance, to be accessible by Flask
bot_instance_global: Optional["EnhancedBot"] = None

# --- Dashboard Routes ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == DASHBOARD_USERNAME and password == DASHBOARD_PASSWORD:
            session["logged_in"] = True
            logger.info(f"User {username} logged in successfully.")
            return redirect(url_for("dashboard_home"))
        else:
            logger.warning(f"Failed login attempt for user {username}.")
            return render_template("login.html", error="Λανθασμένα στοιχεία σύνδεσης")
    return render_template("login.html")

@app.route("/")
def dashboard_home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    bot_status_info = {
        "status": "Online" if bot_instance_global and bot_instance_global.application else "Offline",
        "uptime": "N/A", # Placeholder, needs actual uptime logic
        "active_chats": 0, # Placeholder
        "commands_processed": 0 # Placeholder
    }
    
    crm_stats = None
    sre_stats = None

    if CRM_ENABLED and bot_instance_global and bot_instance_global.crm_module:
        try:
            crm_stats = {"customer_count": len(bot_instance_global.crm_module.customers)}
        except Exception as e:
            logger.error(f"Error accessing CRM stats: {e}")
            crm_stats = {"customer_count": "Error"}

    if SMART_REPLY_ENABLED and bot_instance_global and bot_instance_global.smart_reply_engine:
        try:
            sre_stats = {
                "trigger_count": len(bot_instance_global.smart_reply_engine.triggers),
                "response_count": len(bot_instance_global.smart_reply_engine.responses),
                "mapping_count": len(bot_instance_global.smart_reply_engine.mappings)
            }
        except Exception as e:
            logger.error(f"Error accessing SRE stats: {e}")
            sre_stats = {"trigger_count": "Error", "response_count": "Error", "mapping_count": "Error"}
            
    return render_template("dashboard.html", bot_status=bot_status_info, crm_stats=crm_stats, sre_stats=sre_stats)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    logger.info("User logged out.")
    return redirect(url_for("login"))

# --- Telegram Bot Class and Logic ---
class EnhancedBot:
    def __init__(self, token: str, admin_ids: List[int]):
        self.token = token
        self.admin_ids = admin_ids
        logger.info(f"Initializing EnhancedBot with admin IDs: {admin_ids}")
        self.application = ApplicationBuilder().token(self.token).build()
        
        self.crm_module = CRMModule() if CRM_ENABLED else None
        self.smart_reply_engine = SmartReplyEngine(crm_module=self.crm_module) if SMART_REPLY_ENABLED else None
        
        if self.crm_module:
            logger.info("CRM Module initialized.")
        if self.smart_reply_engine:
            logger.info("Smart Reply Engine initialized.")

        self._setup_handlers()
        logger.info("EnhancedBot components initialized.")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        logger.info(f"Received /start command from user_id: {user_id}")
        await context.bot.send_message(chat_id=user_id, text="Καλώς ήρθατε στο NovaXA Bot! Πληκτρολογήστε /help για λίστα εντολών.")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        logger.info(f"Received /help command from user_id: {user_id}")
        help_text = "Διαθέσιμες εντολές:\n"
        help_text += "/start - Έναρξη συνομιλίας\n"
        help_text += "/help - Εμφάνιση αυτού του μηνύματος\n"
        help_text += "/status - Κατάσταση του bot\n"
        help_text += "/id - Εμφάνιση του User ID σας\n"
        if CRM_ENABLED:
            help_text += "\nCRM Εντολές:\n"
            help_text += "/addcustomer <Όνομα>; <Email>; <TelegramID>; <Κατάσταση>; [Project1,Project2]; [Σημειώσεις] - Προσθήκη πελάτη\n"
            help_text += "/findcustomer <TelegramID | Email | Όνομα> - Εύρεση πελάτη\n"
            help_text += "/updatestatus <TelegramID> <Νέα Κατάσταση> - Ενημέρωση κατάστασης πελάτη\n"
            help_text += "/addnote <TelegramID> <Σημείωση> - Προσθήκη σημείωσης σε πελάτη\n"
        await context.bot.send_message(chat_id=user_id, text=help_text)

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        logger.info(f"Received /status command from user_id: {user_id}")
        crm_status = "Ενεργό" if self.crm_module else "Ανενεργό"
        sre_status = "Ενεργό" if self.smart_reply_engine else "Ανενεργό"
        await context.bot.send_message(chat_id=user_id, text=f"Κατάσταση Bot: Online\nCRM Module: {crm_status}\nSmart Reply Engine: {sre_status}")

    async def id_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        logger.info(f"Received /id command from user_id: {user_id}")
        await context.bot.send_message(chat_id=user_id, text=f"Το User ID σας είναι: {user_id}\nΤο Chat ID είναι: {update.effective_chat.id}")

    async def add_customer_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        if not self.crm_module:
            await context.bot.send_message(chat_id=user_id, text="Η λειτουργία CRM δεν είναι ενεργή.")
            return
        try:
            args_text = " ".join(context.args)
            parts = [p.strip() for p in args_text.split(";")]
            if len(parts) < 4:
                await context.bot.send_message(chat_id=user_id, text="Χρήση: /addcustomer <Όνομα>; <Email>; <TelegramID>; <Κατάσταση>; [Projects]; [Notes]")
                return
            name, email, telegram_id_str, status = parts[0], parts[1], parts[2], parts[3]
            projects = [p.strip() for p in parts[4].split(",")] if len(parts) > 4 and parts[4] else []
            notes = parts[5] if len(parts) > 5 else ""
            success, message = self.crm_module.add_customer(name, email, telegram_id_str, status, projects, notes)
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logger.error(f"Error in add_customer_command: {e}")
            await context.bot.send_message(chat_id=user_id, text=f"Σφάλμα: {e}. Χρήση: /addcustomer <Όνομα>; <Email>; <TelegramID>; <Κατάσταση>; [Projects]; [Notes]")

    async def find_customer_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        if not self.crm_module:
            await context.bot.send_message(chat_id=user_id, text="Η λειτουργία CRM δεν είναι ενεργή.")
            return
        if not context.args:
            await context.bot.send_message(chat_id=user_id, text="Χρήση: /findcustomer <TelegramID | Email | Όνομα>")
            return
        identifier = " ".join(context.args)
        customer_data = self.crm_module.find_customer(identifier, search_by="telegram_id")
        if not customer_data: customer_data = self.crm_module.find_customer(identifier, search_by="email")
        if not customer_data: customer_data = self.crm_module.find_customer(identifier, search_by="name")
        if customer_data:
            response_text = ""
            if isinstance(customer_data, list):
                response_text = "Βρέθηκαν οι εξής πελάτες:\n"
                for cust in customer_data:
                    response_text += f'- ID: {cust.get("telegram_id")}, Όνομα: {cust.get("name")}, Email: {cust.get("email")}\n'
            else:
                response_text = f"Στοιχεία Πελάτη:\n"
                for key, value in customer_data.items():
                    response_text += f'{key.replace("_", " ").capitalize()}: {value}\n'
            await context.bot.send_message(chat_id=user_id, text=response_text)
        else:
            await context.bot.send_message(chat_id=user_id, text="Δεν βρέθηκε πελάτης.")

    async def update_customer_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        if not self.crm_module: await context.bot.send_message(chat_id=user_id, text="Η λειτουργία CRM δεν είναι ενεργή."); return
        if len(context.args) < 2: await context.bot.send_message(chat_id=user_id, text="Χρήση: /updatestatus <TelegramID> <Νέα Κατάσταση>"); return
        telegram_id_to_update, new_status = context.args[0], " ".join(context.args[1:])
        success, message = self.crm_module.update_customer_status(telegram_id_to_update, new_status)
        await context.bot.send_message(chat_id=user_id, text=message)

    async def add_note_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        if not self.crm_module: await context.bot.send_message(chat_id=user_id, text="Η λειτουργία CRM δεν είναι ενεργή."); return
        if len(context.args) < 2: await context.bot.send_message(chat_id=user_id, text="Χρήση: /addnote <TelegramID> <Σημείωση>"); return
        telegram_id_for_note, note_text = context.args[0], " ".join(context.args[1:])
        success, message = self.crm_module.add_note_to_customer(telegram_id_for_note, note_text)
        await context.bot.send_message(chat_id=user_id, text=message)

    async def smart_reply_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id_str = str(update.effective_chat.id)
        text = update.message.text
        logger.info(f"Message from user_id {user_id_str}: {text}")
        if self.smart_reply_engine:
            crm_context = self.crm_module.find_customer(user_id_str) if self.crm_module else None
            response_data = self.smart_reply_engine.process_message(text, user_telegram_id=user_id_str, crm_data=crm_context)
            if response_data and response_data.get("text"):
                await context.bot.send_message(chat_id=user_id_str, text=response_data["text"])
                return
        pass 

    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("id", self.id_command))
        if CRM_ENABLED:
            self.application.add_handler(CommandHandler("addcustomer", self.add_customer_command))
            self.application.add_handler(CommandHandler("findcustomer", self.find_customer_command))
            self.application.add_handler(CommandHandler("updatestatus", self.update_customer_status_command))
            self.application.add_handler(CommandHandler("addnote", self.add_note_command))
            logger.info("CRM command handlers set up.")
        
        if SMART_REPLY_ENABLED:
            self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.smart_reply_handler))
            logger.info("Smart Reply handler set up.")
        else:
            async def default_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Δεν κατάλαβα: {update.message.text}. Πληκτρολογήστε /help.")
            self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), default_text_handler))
            logger.info("Default text handler set up as Smart Reply Engine is disabled.")

        logger.info("Bot handlers set up.")

    def run_bot_polling(self):
        logger.info("Starting bot polling...")
        self.application.run_polling()

# --- Main Execution Logic ---
def run_flask_in_thread():
    logger.info("Starting Flask app in a separate thread.")
    flask_port = int(os.environ.get("PORT", 5000))
    thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=flask_port, use_reloader=False, debug=False))
    thread.daemon = True
    thread.start()
    logger.info(f"Flask app should be running on port {flask_port}")

def main() -> None:
    global bot_instance_global

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    admin_ids_str = os.environ.get("TELEGRAM_ADMIN_IDS")

    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set! Please ensure it is in your .env file or environment.")
        sys.exit(1)
    if not admin_ids_str:
        logger.warning("TELEGRAM_ADMIN_IDS environment variable not set. Some admin functions might be restricted or open.")
        admin_ids = []
    else:
        try:
            admin_ids = [int(admin_id.strip()) for admin_id in admin_ids_str.split(",")]
        except ValueError:
            logger.error("TELEGRAM_ADMIN_IDS is not a valid comma-separated list of integers.")
            admin_ids = []
    
    logger.info(f"Bot Token: {bot_token[:5]}...{bot_token[-5:]}")
    logger.info(f"Admin IDs: {admin_ids}")

    bot_instance_global = EnhancedBot(token=bot_token, admin_ids=admin_ids)
    
    run_flask_in_thread()

    bot_instance_global.run_bot_polling()

if __name__ == "__main__":
    main()

