#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Telegram Bot
--------------------
A comprehensive Telegram bot implementation with advanced features
and integration capabilities.

This module serves as the main entry point for the Telegram bot,
handling command processing, message routing, and user interactions.
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

# Third-party imports
import telegram
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,  # <--- ΑΛΛΑΓΗ ΕΔΩ
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

# Local imports
from api import TelegramAPI, DataProcessor
from integration import ServiceIntegration, NotificationSystem
from monitor import SystemMonitor, PerformanceTracker

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Bot states for conversation handler
MAIN_MENU, SETTINGS, PROCESSING, CONFIRMATION = range(4)

class EnhancedBot:
    """
    Enhanced Telegram Bot with advanced features and integrations.
    
    This class implements a feature-rich Telegram bot with support for:
    - Multi-language support
    - User session management
    - Service integrations
    - Automated notifications
    - Performance monitoring
    - Advanced command processing
    """
    
    def __init__(self, token: str, admin_ids: List[int] = None):
        """
        Initialize the Enhanced Telegram Bot.
        
        Args:
            token: Telegram Bot API token
            admin_ids: List of Telegram user IDs with admin privileges
        """
        self.token = token
        self.admin_ids = admin_ids or []
        self.api = TelegramAPI(token)
        self.integration = ServiceIntegration()
        self.notification = NotificationSystem()
        self.monitor = SystemMonitor()
        self.performance = PerformanceTracker()
        self.data_processor = DataProcessor()
        
        # User session storage
        self.user_sessions = {}
        self.user_settings = {}
        self.active_conversations = {}
        
        # Initialize the application
        self.application = ApplicationBuilder().token(token).build()  # <--- ΑΛΛΑΓΗ ΕΔΩ
        self._setup_handlers()
        
        logger.info("Enhanced Telegram Bot initialized successfully")
    
    def _setup_handlers(self):
        """Set up command and message handlers for the bot."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Admin-only commands
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Conversation handler for multi-step interactions
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("process", self.process_command)],
            states={
                MAIN_MENU: [
                    CallbackQueryHandler(self.menu_selection, pattern="^menu_"),
                ],
                SETTINGS: [
                    CallbackQueryHandler(self.settings_selection, pattern="^setting_"),
                ],
                PROCESSING: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_input),
                ],
                CONFIRMATION: [
                    CallbackQueryHandler(self.confirm_action, pattern="^confirm_"),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel_conversation)],
        )
        self.application.add_handler(conv_handler)
        
        # Default message handler
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        user = update.effective_user
        logger.info(f"User {user.id} started the bot")
        
        # Initialize user session if not exists
        if user.id not in self.user_sessions:
            self.user_sessions[user.id] = {
                "start_time": datetime.now(),
                "language": "en",
                "interactions": 0,
            }
        
        # Increment interaction count
        self.user_sessions[user.id]["interactions"] += 1
        
        # Create welcome message with inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("Help", callback_data="menu_help"),
                InlineKeyboardButton("Settings", callback_data="menu_settings"),
            ],
            [
                InlineKeyboardButton("Features", callback_data="menu_features"),
                InlineKeyboardButton("About", callback_data="menu_about"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(
            f"Hello, <b>{user.first_name}</b>! Welcome to the Enhanced Telegram Bot.\n\n"
            f"This bot provides advanced features and integrations.\n"
            f"Use /help to see available commands or select an option below:",
            reply_markup=reply_markup,
        )
        
        # Log user activity
        self.monitor.log_activity(user.id, "start_command")
        
        return MAIN_MENU
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        user = update.effective_user
        logger.info(f"User {user.id} requested help")
        
        help_text = (
            "Available commands:\n\n"
            "/start - Start the bot and see welcome message\n"
            "/help - Show this help message\n"
            "/settings - Configure your preferences\n"
            "/status - Check bot status and performance\n"
            "/process - Start a multi-step process\n\n"
            "Admin commands:\n"
            "/admin - Access admin panel\n"
            "/broadcast - Send message to all users\n"
            "/stats - View usage statistics"
        )
        
        await update.message.reply_text(help_text)
        
        # Log user activity
        self.monitor.log_activity(user.id, "help_command")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /settings command."""
        user = update.effective_user
        logger.info(f"User {user.id} accessed settings")
        
        # Initialize user settings if not exists
        if user.id not in self.user_settings:
            self.user_settings[user.id] = {
                "language": "en",
                "notifications": True,
                "data_sharing": False,
                "theme": "light",
            }
        
        settings = self.user_settings[user.id]
        
        # Create settings menu with inline keyboard
        keyboard = [
            [
                InlineKeyboardButton(
                    f"Language: {settings['language'].upper()}", 
                    callback_data="setting_language"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"Notifications: {'ON' if settings['notifications'] else 'OFF'}", 
                    callback_data="setting_notifications"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"Data Sharing: {'ON' if settings['data_sharing'] else 'OFF'}", 
                    callback_data="setting_data_sharing"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"Theme: {settings['theme'].capitalize()}", 
                    callback_data="setting_theme"
                ),
            ],
            [
                InlineKeyboardButton("Save Settings", callback_data="setting_save"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Settings Configuration\n\n"
            "Customize your bot experience by adjusting the settings below:",
            reply_markup=reply_markup,
        )
        
        # Log user activity
        self.monitor.log_activity(user.id, "settings_command")
        
        return SETTINGS
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /status command."""
        user = update.effective_user
        logger.info(f"User {user.id} requested status")
        
        # Get system status and performance metrics
        status = self.monitor.get_system_status()
        performance = self.performance.get_metrics()
        
        status_text = (
            "Bot Status and Performance\n\n"
            f"Status: {status['status']}\n"
            f"Uptime: {status['uptime']}\n"
            f"Active Users: {status['active_users']}\n"
            f"Response Time: {performance['response_time']}ms\n"
            f"Memory Usage: {performance['memory_usage']}MB\n"
            f"CPU Usage: {performance['cpu_usage']} %\n\n"
            f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await update.message.reply_text(status_text)
        
        # Log user activity
        self.monitor.log_activity(user.id, "status_command")
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /admin command (admin-only)."""
        user = update.effective_user
        logger.info(f"User {user.id} attempted to access admin panel")
        
        # Check if user has admin privileges
        if user.id not in self.admin_ids:
            await update.message.reply_text(
                "You don't have permission to access the admin panel."
            )
            return
        
        # Create admin panel with inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("User Management", callback_data="admin_users"),
                InlineKeyboardButton("System Settings", callback_data="admin_system"),
            ],
            [
                InlineKeyboardButton("Logs", callback_data="admin_logs"),
                InlineKeyboardButton("Maintenance", callback_data="admin_maintenance"),
            ],
            [
                InlineKeyboardButton("Broadcast Message", callback_data="admin_broadcast"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Admin Panel\n\n"
            "Welcome to the admin panel. Select an option to proceed:",
            reply_markup=reply_markup,
        )
        
        # Log admin activity
        self.monitor.log_activity(user.id, "admin_command", is_admin=True)
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /broadcast command (admin-only)."""
        user = update.effective_user
        logger.info(f"User {user.id} attempted to use broadcast command")
        
        # Check if user has admin privileges
        if user.id not in self.admin_ids:
            await update.message.reply_text(
                "You don't have permission to use the broadcast command."
            )
            return
        
        # Check if message text is provided
        if not context.args:
            await update.message.reply_text(
                "Please provide a message to broadcast.\n"
                "Usage: /broadcast <message>"
            )
            return
        
        # Get broadcast message
        broadcast_message = " ".join(context.args)
        
        # Create confirmation keyboard
        keyboard = [
            [
                InlineKeyboardButton("Confirm", callback_data="confirm_broadcast"),
                InlineKeyboardButton("Cancel", callback_data="confirm_cancel"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Store broadcast message in context
        context.user_data["broadcast_message"] = broadcast_message
        
        await update.message.reply_text(
            f"You are about to broadcast the following message to all users:\n\n"
            f"{broadcast_message}\n\n"
            f"Please confirm or cancel:",
            reply_markup=reply_markup,
        )
        
        # Log admin activity
        self.monitor.log_activity(user.id, "broadcast_command", is_admin=True)
        
        return CONFIRMATION
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /stats command (admin-only)."""
        user = update.effective_user
        logger.info(f"User {user.id} attempted to view stats")
        
        # Check if user has admin privileges
        if user.id not in self.admin_ids:
            await update.message.reply_text(
                "You don't have permission to view statistics."
            )
            return
        
        # Get usage statistics
        stats = self.monitor.get_usage_statistics()
        
        stats_text = (
            "Usage Statistics\n\n"
            f"Total Users: {stats['total_users']}\n"
            f"Active Users (24h): {stats['active_users_24h']}\n"
            f"New Users (7d): {stats['new_users_7d']}\n"
            f"Total Commands: {stats['total_commands']}\n"
            f"Popular Commands: {', '.join(stats['popular_commands'])}\n\n"
            f"Average Response Time: {stats['avg_response_time']}ms\n"
            f"Peak Usage Time: {stats['peak_usage_time']}\n\n"
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await update.message.reply_text(stats_text)
        
        # Log admin activity
        self.monitor.log_activity(user.id, "stats_command", is_admin=True)
    
    async def process_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /process command to start a multi-step process."""
        user = update.effective_user
        logger.info(f"User {user.id} started a process")
        
        # Initialize process data
        context.user_data["process"] = {
            "step": 1,
            "data": {},
            "start_time": datetime.now(),
        }
        
        # Create process menu with inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("Option 1", callback_data="menu_option1"),
                InlineKeyboardButton("Option 2", callback_data="menu_option2"),
            ],
            [
                InlineKeyboardButton("Option 3", callback_data="menu_option3"),
                InlineKeyboardButton("Option 4", callback_data="menu_option4"),
            ],
            [
                InlineKeyboardButton("Cancel", callback_data="menu_cancel"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Process Started\n\n"
            "This is a multi-step process. Please select an option to continue:",
            reply_markup=reply_markup,
        )
        
        # Log user activity
        self.monitor.log_activity(user.id, "process_command")
        
        return MAIN_MENU
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks from inline keyboards."""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        callback_data = query.data
        logger.info(f"User {user.id} pressed button: {callback_data}")
        
        # Handle different callback types
        if callback_data.startswith("menu_"):
            return await self.menu_selection(update, context)
        elif callback_data.startswith("setting_"):
            return await self.settings_selection(update, context)
        elif callback_data.startswith("admin_"):
            return await self.admin_selection(update, context)
        elif callback_data.startswith("confirm_"):
            return await self.confirm_action(update, context)
        else:
            await query.edit_message_text(
                f"Unknown callback: {callback_data}\n"
                f"Please try again or contact support."
            )
    
    async def menu_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle menu selection callbacks."""
        query = update.callback_query
        user = query.from_user
        callback_data = query.data
        
        # Extract menu option
        option = callback_data.replace("menu_", "")
        
        if option == "help":
            await query.edit_message_text(
                "Help Information\n\n"
                "This bot provides various features and commands:\n"
                "- Use /start to begin\n"
                "- Use /help to see available commands\n"
                "- Use /settings to configure preferences\n"
                "- Use /status to check bot status\n"
                "- Use /process to start a multi-step process\n\n"
                "For more assistance, contact support."
            )
        elif option == "settings":
            # Redirect to settings
            await query.edit_message_text("Loading settings...")
            await self.settings_command(update, context)
            return SETTINGS
        elif option == "features":
            await query.edit_message_text(
                "Bot Features\n\n"
                "This enhanced Telegram bot includes:\n"
                "- Multi-language support\n"
                "- User session management\n"
                "- Service integrations\n"
                "- Automated notifications\n"
                "- Performance monitoring\n"
                "- Advanced command processing\n"
                "- Admin controls and statistics\n\n"
                "Explore these features using the available commands."
            )
        elif option == "about":
            await query.edit_message_text(
                "About This Bot\n\n"
                "Enhanced Telegram Bot\n"
                "Version: 1.0.0\n"
                "Created by: Your Organization\n\n"
                "This bot demonstrates advanced Telegram bot capabilities "
                "with a comprehensive architecture and feature set.\n\n"
                "© 2025 Your Organization. All rights reserved."
            )
        elif option == "cancel":
            await query.edit_message_text(
                "Process cancelled. Use /start to begin again."
            )
            return ConversationHandler.END
        elif option in ["option1", "option2", "option3", "option4"]:
            # Store selected option
            context.user_data["process"]["option"] = option
            context.user_data["process"]["step"] = 2
            
            await query.edit_message_text(
                f"You selected Option {option[-1]}.\n\n"
                f"Please enter additional information for processing:"
            )
            return PROCESSING
        else:
            await query.edit_message_text(
                f"Unknown option: {option}\n"
                f"Please try again or use /start to begin again."
            )
        
        # Log user activity
        self.monitor.log_activity(user.id, f"menu_selection_{option}")
        
        return MAIN_MENU
    
    async def settings_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle settings selection callbacks."""
        query = update.callback_query
        user = query.from_user
        callback_data = query.data
        
        # Initialize user settings if not exists
        if user.id not in self.user_settings:
            self.user_settings[user.id] = {
                "language": "en",
                "notifications": True,
                "data_sharing": False,
                "theme": "light",
            }
        
        settings = self.user_settings[user.id]
        
        # Extract setting option
        option = callback_data.replace("setting_", "")
        
        if option == "language":
            # Toggle language (simplified for demo)
            languages = ["en", "es", "fr", "de"]
            current_index = languages.index(settings["language"])
            next_index = (current_index + 1) % len(languages)
            settings["language"] = languages[next_index]
        elif option == "notifications":
            # Toggle notifications
            settings["notifications"] = not settings["notifications"]
        elif option == "data_sharing":
            # Toggle data sharing
            settings["data_sharing"] = not settings["data_sharing"]
        elif option == "theme":
            # Toggle theme
            settings["theme"] = "dark" if settings["theme"] == "light" else "light"
        elif option == "save":
            # Save settings
            await query.edit_message_text(
                "Settings saved successfully!\n\n"
                f"Language: {settings['language'].upper()}\n"
                f"Notifications: {'ON' if settings['notifications'] else 'OFF'}\n"
                f"Data Sharing: {'ON' if settings['data_sharing'] else 'OFF'}\n"
                f"Theme: {settings['theme'].capitalize()}\n\n"
                f"Use /start to return to the main menu."
            )
            
            # Log settings update
            self.monitor.log_activity(user.id, "settings_saved")
            
            return ConversationHandler.END
        else:
            await query.edit_message_text(
                f"Unknown setting: {option}\n"
                f"Please try again or use /settings to start over."
            )
            return SETTINGS
        
        # Update settings display
        keyboard = [
            [
                InlineKeyboardButton(
                    f"Language: {settings['language'].upper()}", 
                    callback_data="setting_language"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"Notifications: {'ON' if settings['notifications'] else 'OFF'}", 
                    callback_data="setting_notifications"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"Data Sharing: {'ON' if settings['data_sharing'] else 'OFF'}", 
                    callback_data="setting_data_sharing"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"Theme: {settings['theme'].capitalize()}", 
                    callback_data="setting_theme"
                ),
            ],
            [
                InlineKeyboardButton("Save Settings", callback_data="setting_save"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Settings Configuration\n\n"
            "Customize your bot experience by adjusting the settings below:",
            reply_markup=reply_markup,
        )
        
        # Log setting change
        self.monitor.log_activity(user.id, f"setting_changed_{option}")
        
        return SETTINGS
    
    async def admin_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin panel selection callbacks."""
        query = update.callback_query
        user = query.from_user
        callback_data = query.data
        
        # Check if user has admin privileges
        if user.id not in self.admin_ids:
            await query.edit_message_text(
                "You don't have permission to access the admin panel."
            )
            return
        
        # Extract admin option
        option = callback_data.replace("admin_", "")
        
        if option == "users":
            # Get user statistics
            user_stats = self.monitor.get_user_statistics()
            
            await query.edit_message_text(
                "User Management\n\n"
                f"Total Users: {user_stats['total_users']}\n"
                f"Active Users: {user_stats['active_users']}\n"
                f"New Users (24h): {user_stats['new_users_24h']}\n\n"
                f"Top Users:\n{user_stats['top_users_formatted']}\n\n"
                f"Use /admin to return to the admin panel."
            )
        elif option == "system":
            # Get system settings
            system_settings = self.monitor.get_system_settings()
            
            await query.edit_message_text(
                "System Settings\n\n"
                f"Max Connections: {system_settings['max_connections']}\n"
                f"Timeout: {system_settings['timeout']}s\n"
                f"Rate Limit: {system_settings['rate_limit']}/min\n"
                f"Maintenance Mode: {'ON' if system_settings['maintenance_mode'] else 'OFF'}\n\n"
                f"Use /admin to return to the admin panel."
            )
        elif option == "logs":
            # Get recent logs
            recent_logs = self.monitor.get_recent_logs(10)
            
            logs_text = "Recent Logs\n\n"
            for log in recent_logs:
                logs_text += f"{log['timestamp']} - {log['level']} - {log['message']}\n"
            
            logs_text += "\nUse /admin to return to the admin panel."
            
            await query.edit_message_text(logs_text)
        elif option == "maintenance":
            # Toggle maintenance mode
            current_mode = self.monitor.toggle_maintenance_mode()
            
            await query.edit_message_text(
                "Maintenance Mode\n\n"
                f"Maintenance mode is now {'ON' if current_mode else 'OFF'}.\n\n"
                f"When maintenance mode is ON, only admins can access the bot.\n\n"
                f"Use /admin to return to the admin panel."
            )
        elif option == "broadcast":
            # Redirect to broadcast command
            await query.edit_message_text(
                "Broadcast Message\n\n"
                "Use the /broadcast command followed by your message to send "
                "a broadcast to all users.\n\n"
                "Example: /broadcast System maintenance scheduled for tomorrow."
            )
        else:
            await query.edit_message_text(
                f"Unknown admin option: {option}\n"
                f"Please try again or use /admin to start over."
            )
        
        # Log admin activity
        self.monitor.log_activity(user.id, f"admin_selection_{option}", is_admin=True)
    
    async def confirm_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle confirmation callbacks."""
        query = update.callback_query
        user = query.from_user
        callback_data = query.data
        
        # Extract confirmation option
        option = callback_data.replace("confirm_", "")
        
        if option == "broadcast":
            # Check if user has admin privileges
            if user.id not in self.admin_ids:
                await query.edit_message_text(
                    "You don't have permission to broadcast messages."
                )
                return ConversationHandler.END
            
            # Get broadcast message from context
            broadcast_message = context.user_data.get("broadcast_message", "")
            
            if not broadcast_message:
                await query.edit_message_text(
                    "Error: Broadcast message not found.\n"
                    "Please try again using /broadcast command."
                )
                return ConversationHandler.END
            
            # Simulate broadcasting (in a real bot, this would send to all users)
            await query.edit_message_text(
                "Broadcasting message to all users...\n\n"
                f"Message: {broadcast_message}\n\n"
                f"This may take some time depending on the number of users."
            )
            
            # Log admin activity
            self.monitor.log_activity(user.id, "broadcast_confirmed", is_admin=True)
        elif option == "cancel":
            await query.edit_message_text(
                "Action cancelled.\n\n"
                "Use /start to return to the main menu."
            )
        else:
            await query.edit_message_text(
                f"Unknown confirmation: {option}\n"
                f"Please try again or use /start to begin again."
            )
        
        return ConversationHandler.END
    
    async def process_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process user input during a multi-step process."""
        user = update.effective_user
        user_input = update.message.text
        logger.info(f"User {user.id} provided input: {user_input}")
        
        # Get process data
        process = context.user_data.get("process", {})
        step = process.get("step", 1)
        
        if step == 2:
            # Store user input
            process["input"] = user_input
            process["step"] = 3
            
            # Create confirmation keyboard
            keyboard = [
                [
                    InlineKeyboardButton("Confirm", callback_data="confirm_process"),
                    InlineKeyboardButton("Cancel", callback_data="confirm_cancel"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Process Summary\n\n"
                f"Option: {process.get('option', 'Unknown')}\n"
                f"Input: {user_input}\n\n"
                f"Please confirm to proceed or cancel:",
                reply_markup=reply_markup,
            )
            
            # Log user activity
            self.monitor.log_activity(user.id, "process_input_provided")
            
            return CONFIRMATION
        else:
            await update.message.reply_text(
                "Error: Invalid process step.\n"
                "Please use /process to start over."
            )
            return ConversationHandler.END
    
    async def cancel_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the current conversation."""
        user = update.effective_user
        logger.info(f"User {user.id} cancelled conversation")
        
        await update.message.reply_text(
            "Process cancelled.\n\n"
            "Use /start to begin again."
        )
        
        # Log user activity
        self.monitor.log_activity(user.id, "conversation_cancelled")
        
        return ConversationHandler.END
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user = update.effective_user
        message_text = update.message.text
        logger.info(f"User {user.id} sent message: {message_text}")
        
        # Process message using data processor
        response = self.data_processor.process_message(message_text)
        
        await update.message.reply_text(response)
        
        # Log user activity
        self.monitor.log_activity(user.id, "message_processed")
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the dispatcher."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Send error message to user if possible
        if update and isinstance(update, Update) and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="An error occurred while processing your request. Please try again later."
            )
        
        # Log error
        self.monitor.log_error(str(context.error))
    
    def run(self, webhook_mode: bool = False, webhook_url: str = None, port: int = 8443):
        """
        Run the bot either in polling mode or webhook mode.
        
        Args:
            webhook_mode: Whether to use webhook mode instead of polling
            webhook_url: Webhook URL (required if webhook_mode is True)
            port: Port to listen on for webhook mode
        """
        logger.info("Starting Enhanced Telegram Bot")
        
        if webhook_mode:
            if not webhook_url:
                raise ValueError("Webhook URL is required for webhook mode")
            
            # Start webhook
            self.application.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=self.token,
                webhook_url=f"{webhook_url}/{self.token}"
            )
            logger.info(f"Bot started in webhook mode on port {port}")
        else:
            # Start polling
            self.application.run_polling()
            logger.info("Bot started in polling mode")


def main():
    """Main function to run the bot."""
    # Get bot token from environment variable
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        sys.exit(1)
    
    # Get admin IDs from environment variable (comma-separated)
    admin_ids_str = os.environ.get("TELEGRAM_ADMIN_IDS", "")
    admin_ids = [int(id_str) for id_str in admin_ids_str.split(",") if id_str.strip()]
    
    # Create and run the bot
    bot = EnhancedBot(token, admin_ids)
    
    # Check if webhook mode is enabled
    webhook_mode = os.environ.get("WEBHOOK_MODE", "false").lower() == "true"
    webhook_url = os.environ.get("WEBHOOK_URL", "")
    webhook_port = int(os.environ.get("WEBHOOK_PORT", "8443"))
    
    try:
        bot.run(webhook_mode=webhook_mode, webhook_url=webhook_url, port=webhook_port)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

