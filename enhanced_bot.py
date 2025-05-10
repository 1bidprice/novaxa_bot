#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Telegram Bot & Dashboard
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

# Local imports
from api import TelegramAPI, DataProcessor
from integration import ServiceIntegration, NotificationSystem # Βεβαιωθείτε ότι αυτό το αρχείο θα διορθωθεί όπως είπαμε παραπάνω
from monitor import SystemMonitor, PerformanceTracker

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Flask App Definition (Global) ---
# Προσθήκη template_folder='templates'
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "please_change_this_in_production_and_render_env_vars")

# Environment variables for dashboard credentials
DASHBOARD_USERNAME = os.environ.get("DASHBOARD_USERNAME", "admin")
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "password")

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
            return "Λανθασμένα στοιχεία σύνδεσης", 401
    return render_template("login.html")

@app.route("/")
def dashboard_home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    bot_status_info = {
        "status": "Έλεγχος...",
        "uptime": "N/A",
        "active_chats": 0,
        "commands_processed": 0
    }
    return render_template("dashboard.html", bot_status=bot_status_info)

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
        self._setup_handlers()
        self.api_handler = TelegramAPI(self.token)
        self.data_processor = DataProcessor()
        self.service_integrator = ServiceIntegration()
        # ΣΗΜΑΝΤΙΚΟ: Η NotificationSystem πρέπει να διορθωθεί στο integration.py
        # για να μην περνάει το bot object ως config file.
        # Πιθανώς χρειάζεται: NotificationSystem(bot_instance=self.application.bot, config_path="your_config.json")
        # ή απλά NotificationSystem(bot_instance=self.application.bot) αν δεν παίρνει config αρχείο.
        self.notification_sys = NotificationSystem(self.application.bot) 
        self.system_monitor = SystemMonitor()
        self.performance_tracker = PerformanceTracker()
        logger.info("EnhancedBot components initialized.")

    def _setup_handlers(self):
        start_handler = CommandHandler("start", self.start)
        self.application.add_handler(start_handler)
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.echo)
        self.application.add_handler(echo_handler)
        logger.info("Bot handlers set up.")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        logger.info(f"Received /start command from user_id: {user_id}")
        await context.bot.send_message(chat_id=user_id, text="Καλώς ήρθατε στο NovaXA Bot!")

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        text = update.message.text
        logger.info(f"Echoing message from user_id {user_id}: {text}")
        await context.bot.send_message(chat_id=user_id, text=text)

    def run_bot_polling(self):
        logger.info("Starting bot in polling mode...")
        self.application.run_polling()
        logger.info("Bot polling stopped.")

def start_telegram_bot_logic():
    logger.info("Attempting to start Telegram bot logic (polling)...")
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set. Bot cannot start.")
        return

    admin_ids_str = os.environ.get("TELEGRAM_ADMIN_IDS", "")
    admin_ids = [int(id_str) for id_str in admin_ids_str.split(",") if id_str.strip()]

    try:
        bot_instance = EnhancedBot(token=bot_token, admin_ids=admin_ids)
        bot_instance.run_bot_polling()
    except Exception as e:
        logger.error(f"Error during Telegram bot initialization or polling: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("enhanced_bot.py executed directly. Starting Telegram bot logic.")
    start_telegram_bot_logic()

logger.info("enhanced_bot.py loaded. Flask 'app' object is available for Gunicorn.")

