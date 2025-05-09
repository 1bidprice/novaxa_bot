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
    
    def save_config(self, config_file: str) -> bool:
        """
        Save configuration to a file.
        
        Args:
            config_file: Path to save configuration file
            
        Returns:
            True if configuration was saved successfully, False otherwise
        """
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Saved configuration to {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def register_service(self, service_name: str, service_config: Dict) -> bool:
        """
        Register a new service.
        
        Args:
            service_name: Name of the service
            service_config: Configuration for the service
            
        Returns:
            True if service was registered successfully, False otherwise
        """
        try:
            # Add service to configuration
            if "services" not in self.config:
                self.config["services"] = {}
            
            self.config["services"][service_name] = service_config
            
            # Initialize service if enabled
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
        """
        Enable a service.
        
        Args:
            service_name: Name of the service to enable
            
        Returns:
            True if service was enabled successfully, False otherwise
        """
        if service_name not in self.config.get("services", {}):
            logger.error(f"Service not found: {service_name}")
            return False
        
        try:
            # Enable service in configuration
            self.config["services"][service_name]["enabled"] = True
            
            # Initialize service
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
        """
        Disable a service.
        
        Args:
            service_name: Name of the service to disable
            
        Returns:
            True if service was disabled successfully, False otherwise
        """
        if service_name not in self.config.get("services", {}):
            logger.error(f"Service not found: {service_name}")
            return False
        
        try:
            # Disable service in configuration
            self.config["services"][service_name]["enabled"] = False
            
            # Remove service from active services
            if service_name in self.services:
                del self.services[service_name]
            
            logger.info(f"Disabled service: {service_name}")
            return True
        except Exception as e:
            logger.error(f"Error disabling service: {e}")
            return False
    
    def get_service_status(self, service_name: str) -> Dict:
        """
        Get status of a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service status information
        """
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
        """
        Check if a service is available and working.
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            Service status information
        """
        if service_name not in self.services:
            return {
                "status": "disabled",
                "error": "Service not enabled",
            }
        
        service = self.services[service_name]
        service_config = service.get("config", {})
        
        # Update last check time
        service["last_check"] = datetime.now().isoformat()
        
        # Check service based on type
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
        """
        Check if an HTTP service is available.
        
        Args:
            service_name: Name of the service
            service_config: Service configuration
            
        Returns:
            Service status information
        """
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
        """
        Check if an SMTP service is available.
        
        Args:
            service_name: Name of the service
            service_config: Service configuration
            
        Returns:
            Service status information
        """
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
        """
        Check if a database service is available.
        
        Args:
            service_name: Name of the service
            service_config: Service configuration
            
        Returns:
            Service status information
        """
        db_type = service_config.get("db_type", "")
        host = service_config.get("host", "")
        port = service_config.get("port", 0)
        database = service_config.get("database", "")
        username = service_config.get("username", "")
        password = service_config.get("password", "")
        timeout = service_config.get("timeout", 10)
        
        if not db_type or not host or not port:
            self.services[service_name]["status"] = "error"
            return {
                "status": "error",
                "error": "Incomplete database configuration",
            }
        
        try:
            start_time = time.time()
            
            # Check database connection based on type
            if db_type.lower() == "mysql":
                try:
                    import mysql.connector
                    conn = mysql.connector.connect(
                        host=host,
                        port=port,
                        database=database,
                        user=username,
                        password=password,
                        connect_timeout=timeout,
                    )
                    conn.close()
                except ImportError:
                    return {
                        "status": "error",
                        "error": "MySQL connector not installed",
                    }
            elif db_type.lower() == "postgresql":
                try:
                    import psycopg2
                    conn = psycopg2.connect(
                        host=host,
                        port=port,
                        dbname=database,
                        user=username,
                        password=password,
                        connect_timeout=timeout,
                    )
                    conn.close()
                except ImportError:
                    return {
                        "status": "error",
                        "error": "psycopg2 not installed",
                    }
            elif db_type.lower() == "mongodb":
                try:
                    import pymongo
                    client = pymongo.MongoClient(
                        host=host,
                        port=port,
                        username=username,
                        password=password,
                        serverSelectionTimeoutMS=timeout * 1000,
                    )
                    client.server_info()
                    client.close()
                except ImportError:
                    return {
                        "status": "error",
                        "error": "pymongo not installed",
                    }
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported database type: {db_type}",
                }
            
            response_time = time.time() - start_time
            
            self.services[service_name]["status"] = "ok"
            return {
                "status": "ok",
                "response_time": response_time,
            }
        except Exception as e:
            self.services[service_name]["status"] = "error"
            return {
                "status": "error",
                "error": str(e),
            }
    
    def call_service(self, service_name: str, method: str, **kwargs) -> Dict:
        """
        Call a method on a service.
        
        Args:
            service_name: Name of the service
            method: Method to call
            **kwargs: Additional arguments for the method
            
        Returns:
            Result of the service call
        """
        if service_name not in self.services:
            return {
                "status": "error",
                "error": f"Service not enabled: {service_name}",
            }
        
        service = self.services[service_name]
        service_config = service.get("config", {})
        service_type = service_config.get("type", "")
        
        # Call service method based on type
        if service_type == "http":
            if method == "request":
                return self._http_request(service_name, **kwargs)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown method for HTTP service: {method}",
                }
        elif service_type == "smtp":
            if method == "send_email":
                return self._send_email(service_name, **kwargs)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown method for SMTP service: {method}",
                }
        elif service_type == "database":
            if method == "query":
                return self._database_query(service_name, **kwargs)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown method for database service: {method}",
                }
        else:
            return {
                "status": "error",
                "error": f"Unknown service type: {service_type}",
            }
    
    def _http_request(self, service_name: str, **kwargs) -> Dict:
        """
        Make an HTTP request to a service.
        
        Args:
            service_name: Name of the service
            **kwargs: Additional arguments for the request
            
        Returns:
            Result of the HTTP request
        """
        service_config = self.services[service_name].get("config", {})
        
        # Get base URL from service configuration
        base_url = service_config.get("url", "")
        
        # Get request parameters
        url = kwargs.get("url", "")
        method = kwargs.get("method", "GET")
        headers = {**service_config.get("headers", {}), **kwargs.get("headers", {})}
        params = kwargs.get("params", {})
        data = kwargs.get("data", None)
        json_data = kwargs.get("json", None)
        timeout = kwargs.get("timeout", service_config.get("timeout", 10))
        
        # Combine base URL and endpoint URL if both provided
        if base_url and url and not url.startswith(("http://", "https://")):
            if base_url.endswith("/") and url.startswith("/"):
                url = base_url + url[1:]
            elif not base_url.endswith("/") and not url.startswith("/"):
                url = base_url + "/" + url
            else:
                url = base_url + url
        elif not url:
            url = base_url
        
        if not url:
            return {
                "status": "error",
                "error": "URL not specified",
            }
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=timeout,
            )
            
            # Try to parse response as JSON
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
            
            return {
                "status": "ok",
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response_data,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def _send_email(self, service_name: str, **kwargs) -> Dict:
        """
        Send an email using an SMTP service.
        
        Args:
            service_name: Name of the service
            **kwargs: Additional arguments for sending the email
            
        Returns:
            Result of sending the email
        """
        service_config = self.services[service_name].get("config", {})
        
        # Get SMTP configuration
        host = service_config.get("host", "")
        port = service_config.get("port", 587)
        use_tls = service_config.get("use_tls", True)
        username = service_config.get("username", "")
        password = service_config.get("password", "")
        
        # Get email parameters
        sender = kwargs.get("sender", username)
        recipients = kwargs.get("recipients", [])
        subject = kwargs.get("subject", "")
        body = kwargs.get("body", "")
        html = kwargs.get("html", None)
        
        if not host:
            return {
                "status": "error",
                "error": "SMTP host not specified",
            }
        
        if not sender:
            return {
                "status": "error",
                "error": "Sender not specified",
            }
        
        if not recipients:
            return {
                "status": "error",
                "error": "Recipients not specified",
            }
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = ", ".join(recipients)
            
            # Attach text body
            msg.attach(MIMEText(body, "plain"))
            
            # Attach HTML body if provided
            if html:
                msg.attach(MIMEText(html, "html"))
            
            # Connect to SMTP server and send email
            server = smtplib.SMTP(host, port)
            
            if use_tls:
                server.starttls()
            
            if username and password:
                server.login(username, password)
            
            server.sendmail(sender, recipients, msg.as_string())
            server.quit()
            
            return {
                "status": "ok",
                "message": "Email sent successfully",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def _database_query(self, service_name: str, **kwargs) -> Dict:
        """
        Execute a query on a database service.
        
        Args:
            service_name: Name of the service
            **kwargs: Additional arguments for the query
            
        Returns:
            Result of the database query
        """
        service_config = self.services[service_name].get("config", {})
        
        # Get database configuration
        db_type = service_config.get("db_type", "")
        host = service_config.get("host", "")
        port = service_config.get("port", 0)
        database = service_config.get("database", "")
        username = service_config.get("username", "")
        password = service_config.get("password", "")
        
        # Get query parameters
        query = kwargs.get("query", "")
        params = kwargs.get("params", [])
        
        if not db_type or not host or not port:
            return {
                "status": "error",
                "error": "Incomplete database configuration",
            }
        
        if not query:
            return {
                "status": "error",
                "error": "Query not specified",
            }
        
        try:
            # Execute query based on database type
            if db_type.lower() == "mysql":
                try:
                    import mysql.connector
                    conn = mysql.connector.connect(
                        host=host,
                        port=port,
                        database=database,
                        user=username,
                        password=password,
                    )
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute(query, params)
                    
                    if query.strip().upper().startswith(("SELECT", "SHOW")):
                        result = cursor.fetchall()
                    else:
                        conn.commit()
                        result = {"affected_rows": cursor.rowcount}
                    
                    cursor.close()
                    conn.close()
                    
                    return {
                        "status": "ok",
                        "result": result,
                    }
                except ImportError:
                    return {
                        "status": "error",
                        "error": "MySQL connector not installed",
                    }
            elif db_type.lower() == "postgresql":
                try:
                    import psycopg2
                    import psycopg2.extras
                    
                    conn = psycopg2.connect(
                        host=host,
                        port=port,
                        dbname=database,
                        user=username,
                        password=password,
                    )
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    cursor.execute(query, params)
                    
                    if query.strip().upper().startswith(("SELECT", "SHOW")):
                        result = [dict(row) for row in cursor.fetchall()]
                    else:
                        conn.commit()
                        result = {"affected_rows": cursor.rowcount}
                    
                    cursor.close()
                    conn.close()
                    
                    return {
                        "status": "ok",
                        "result": result,
                    }
                except ImportError:
                    return {
                        "status": "error",
                        "error": "psycopg2 not installed",
                    }
            elif db_type.lower() == "mongodb":
                try:
                    import pymongo
                    import json
                    
                    client = pymongo.MongoClient(
                        host=host,
                        port=port,
                        username=username,
                        password=password,
                    )
                    
                    # Parse query as JSON
                    query_obj = json.loads(query)
                    
                    # Get database and collection
                    db_name = query_obj.get("db", database)
                    collection_name = query_obj.get("collection", "")
                    operation = query_obj.get("operation", "")
                    filter_obj = query_obj.get("filter", {})
                    update_obj = query_obj.get("update", {})
                    options = query_obj.get("options", {})
                    
                    if not collection_name or not operation:
                        return {
                            "status": "error",
                            "error": "Collection or operation not specified",
                        }
                    
                    db = client[db_name]
                    collection = db[collection_name]
                    
                    # Execute operation
                    if operation == "find":
                        result = list(collection.find(filter_obj, **options))
                        # Convert ObjectId to string for JSON serialization
                        for doc in result:
                            if "_id" in doc:
                                doc["_id"] = str(doc["_id"])
                    elif operation == "findOne":
                        result = collection.find_one(filter_obj, **options)
                        if result and "_id" in result:
                            result["_id"] = str(result["_id"])
                    elif operation == "insert":
                        result = collection.insert_one(filter_obj)
                        result = {"inserted_id": str(result.inserted_id)}
                    elif operation == "update":
                        result = collection.update_one(filter_obj, update_obj, **options)
                        result = {
                            "matched_count": result.matched_count,
                            "modified_count": result.modified_count,
                        }
                    elif operation == "delete":
                        result = collection.delete_one(filter_obj)
                        result = {"deleted_count": result.deleted_count}
                    else:
                        return {
                            "status": "error",
                            "error": f"Unsupported operation: {operation}",
                        }
                    
                    client.close()
                    
                    return {
                        "status": "ok",
                        "result": result,
                    }
                except ImportError:
                    return {
                        "status": "error",
                        "error": "pymongo not installed",
                    }
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported database type: {db_type}",
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }


class NotificationSystem:
    """
    Handles notifications for the Telegram bot.
    
    This class provides methods for sending notifications to users
    through various channels.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the notification system.
        
        Args:
            config_file: Path to configuration file for notifications
        """
        self.config = {}
        self.channels = {}
        self.service_integration = ServiceIntegration()
        
        # Load configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        
        logger.info("Notification system initialized")
    
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
            
            # Initialize channels based on configuration
            for channel_name, channel_config in self.config.get("channels", {}).items():
                if channel_config.get("enabled", False):
                    self.channels[channel_name] = {
                        "config": channel_config,
                        "status": "initialized",
                    }
            
            logger.info(f"Loaded notification configuration from {config_file}")
            logger.info(f"Enabled channels: {', '.join(self.channels.keys())}")
            return True
        except Exception as e:
            logger.error(f"Error loading notification configuration: {e}")
            return False
    
    def save_config(self, config_file: str) -> bool:
        """
        Save configuration to a file.
        
        Args:
            config_file: Path to save configuration file
            
        Returns:
            True if configuration was saved successfully, False otherwise
        """
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Saved notification configuration to {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving notification configuration: {e}")
            return False
    
    def register_channel(self, channel_name: str, channel_config: Dict) -> bool:
        """
        Register a new notification channel.
        
        Args:
            channel_name: Name of the channel
            channel_config: Configuration for the channel
            
        Returns:
            True if channel was registered successfully, False otherwise
        """
        try:
            # Add channel to configuration
            if "channels" not in self.config:
                self.config["channels"] = {}
            
            self.config["channels"][channel_name] = channel_config
            
            # Initialize channel if enabled
            if channel_config.get("enabled", False):
                self.channels[channel_name] = {
                    "config": channel_config,
                    "status": "initialized",
                }
            
            logger.info(f"Registered notification channel: {channel_name}")
            return True
        except Exception as e:
            logger.error(f"Error registering notification channel: {e}")
            return False
    
    def enable_channel(self, channel_name: str) -> bool:
        """
        Enable a notification channel.
        
        Args:
            channel_name: Name of the channel to enable
            
        Returns:
            True if channel was enabled successfully, False otherwise
        """
        if channel_name not in self.config.get("channels", {}):
            logger.error(f"Notification channel not found: {channel_name}")
            return False
        
        try:
            # Enable channel in configuration
            self.config["channels"][channel_name]["enabled"] = True
            
            # Initialize channel
            self.channels[channel_name] = {
                "config": self.config["channels"][channel_name],
                "status": "initialized",
            }
            
            logger.info(f"Enabled notification channel: {channel_name}")
            return True
        except Exception as e:
            logger.error(f"Error enabling notification channel: {e}")
            return False
    
    def disable_channel(self, channel_name: str) -> bool:
        """
        Disable a notification channel.
        
        Args:
            channel_name: Name of the channel to disable
            
        Returns:
            True if channel was disabled successfully, False otherwise
        """
        if channel_name not in self.config.get("channels", {}):
            logger.error(f"Notification channel not found: {channel_name}")
            return False
        
        try:
            # Disable channel in configuration
            self.config["channels"][channel_name]["enabled"] = False
            
            # Remove channel from active channels
            if channel_name in self.channels:
                del self.channels[channel_name]
            
            logger.info(f"Disabled notification channel: {channel_name}")
            return True
        except Exception as e:
            logger.error(f"Error disabling notification channel: {e}")
            return False
    
    def send_notification(self, message: str, channel: str = None, **kwargs) -> Dict:
        """
        Send a notification through one or all channels.
        
        Args:
            message: Notification message
            channel: Specific channel to use (if None, use all enabled channels)
            **kwargs: Additional parameters for the notification
            
        Returns:
            Result of sending the notification
        """
        if not message:
            return {
                "status": "error",
                "error": "Message not specified",
            }
        
        # Send to specific channel if provided
        if channel:
            if channel not in self.channels:
                return {
                    "status": "error",
                    "error": f"Channel not enabled: {channel}",
                }
            
            return self._send_to_channel(channel, message, **kwargs)
        
        # Send to all enabled channels
        results = {}
        for channel_name in self.channels:
            results[channel_name] = self._send_to_channel(channel_name, message, **kwargs)
        
        # Check if any channel succeeded
        success = any(result.get("status") == "ok" for result in results.values())
        
        if success:
            return {
                "status": "ok",
                "results": results,
            }
        else:
            return {
                "status": "error",
                "error": "Failed to send notification through any channel",
                "results": results,
            }
    
    def _send_to_channel(self, channel_name: str, message: str, **kwargs) -> Dict:
        """
        Send a notification through a specific channel.
        
        Args:
            channel_name: Name of the channel
            message: Notification message
            **kwargs: Additional parameters for the notification
            
        Returns:
            Result of sending the notification
        """
        channel = self.channels.get(channel_name, {})
        channel_config = channel.get("config", {})
        channel_type = channel_config.get("type", "")
        
        # Send notification based on channel type
        if channel_type == "email":
            return self._send_email_notification(channel_config, message, **kwargs)
        elif channel_type == "telegram":
            return self._send_telegram_notification(channel_config, message, **kwargs)
        elif channel_type == "webhook":
            return self._send_webhook_notification(channel_config, message, **kwargs)
        elif channel_type == "sms":
            return self._send_sms_notification(channel_config, message, **kwargs)
        else:
            return {
                "status": "error",
                "error": f"Unknown channel type: {channel_type}",
            }
    
    def _send_email_notification(self, channel_config: Dict, message: str, **kwargs) -> Dict:
        """
        Send a notification through email.
        
        Args:
            channel_config: Channel configuration
            message: Notification message
            **kwargs: Additional parameters for the notification
            
        Returns:
            Result of sending the notification
        """
        # Get email configuration
        service_name = channel_config.get("service_name", "")
        sender = channel_config.get("sender", "")
        recipients = channel_config.get("recipients", [])
        subject_prefix = channel_config.get("subject_prefix", "[Notification]")
        
        # Get email parameters
        subject = kwargs.get("subject", "Notification")
        html = kwargs.get("html", None)
        
        if subject_prefix:
            subject = f"{subject_prefix} {subject}"
        
        if not service_name:
            # Use direct SMTP configuration
            host = channel_config.get("host", "")
            port = channel_config.get("port", 587)
            use_tls = channel_config.get("use_tls", True)
            username = channel_config.get("username", "")
            password = channel_config.get("password", "")
            
            if not host:
                return {
                    "status": "error",
                    "error": "SMTP host not specified",
                }
            
            if not sender:
                sender = username
            
            if not sender:
                return {
                    "status": "error",
                    "error": "Sender not specified",
                }
            
            if not recipients:
                return {
                    "status": "error",
                    "error": "Recipients not specified",
                }
            
            try:
                # Create message
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = sender
                msg["To"] = ", ".join(recipients)
                
                # Attach text body
                msg.attach(MIMEText(message, "plain"))
                
                # Attach HTML body if provided
                if html:
                    msg.attach(MIMEText(html, "html"))
                
                # Connect to SMTP server and send email
                server = smtplib.SMTP(host, port)
                
                if use_tls:
                    server.starttls()
                
                if username and password:
                    server.login(username, password)
                
                server.sendmail(sender, recipients, msg.as_string())
                server.quit()
                
                return {
                    "status": "ok",
                    "message": "Email notification sent successfully",
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                }
        else:
            # Use service integration
            return self.service_integration.call_service(
                service_name=service_name,
                method="send_email",
                sender=sender,
                recipients=recipients,
                subject=subject,
                body=message,
                html=html,
            )
    
    def _send_telegram_notification(self, channel_config: Dict, message: str, **kwargs) -> Dict:
        """
        Send a notification through Telegram.
        
        Args:
            channel_config: Channel configuration
            message: Notification message
            **kwargs: Additional parameters for the notification
            
        Returns:
            Result of sending the notification
        """
        # Get Telegram configuration
        token = channel_config.get("token", "")
        chat_ids = channel_config.get("chat_ids", [])
        parse_mode = channel_config.get("parse_mode", "HTML")
        
        if not token:
            return {
                "status": "error",
                "error": "Telegram token not specified",
            }
        
        if not chat_ids:
            return {
                "status": "error",
                "error": "Telegram chat IDs not specified",
            }
        
        try:
            from telegram import Bot
            
            # Create bot instance
            bot = Bot(token=token)
            
            # Send message to all chat IDs
            results = {}
            for chat_id in chat_ids:
                try:
                    sent_message = bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=parse_mode,
                    )
                    results[chat_id] = {
                        "status": "ok",
                        "message_id": sent_message.message_id,
                    }
                except Exception as e:
                    results[chat_id] = {
                        "status": "error",
                        "error": str(e),
                    }
            
            # Check if any message was sent successfully
            success = any(result.get("status") == "ok" for result in results.values())
            
            if success:
                return {
                    "status": "ok",
                    "results": results,
                }
            else:
                return {
                    "status": "error",
                    "error": "Failed to send Telegram notification to any chat",
                    "results": results,
                }
        except ImportError:
            return {
                "status": "error",
                "error": "python-telegram-bot not installed",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def _send_webhook_notification(self, channel_config: Dict, message: str, **kwargs) -> Dict:
        """
        Send a notification through a webhook.
        
        Args:
            channel_config: Channel configuration
            message: Notification message
            **kwargs: Additional parameters for the notification
            
        Returns:
            Result of sending the notification
        """
        # Get webhook configuration
        url = channel_config.get("url", "")
        method = channel_config.get("method", "POST")
        headers = channel_config.get("headers", {})
        include_timestamp = channel_config.get("include_timestamp", True)
        
        if not url:
            return {
                "status": "error",
                "error": "Webhook URL not specified",
            }
        
        try:
            # Prepare payload
            payload = {
                "message": message,
            }
            
            # Add timestamp if requested
            if include_timestamp:
                payload["timestamp"] = datetime.now().isoformat()
            
            # Add additional parameters
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            # Send webhook request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=payload,
            )
            
            response.raise_for_status()
            
            return {
                "status": "ok",
                "status_code": response.status_code,
                "message": "Webhook notification sent successfully",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def _send_sms_notification(self, channel_config: Dict, message: str, **kwargs) -> Dict:
        """
        Send a notification through SMS.
        
        Args:
            channel_config: Channel configuration
            message: Notification message
            **kwargs: Additional parameters for the notification
            
        Returns:
            Result of sending the notification
        """
        # Get SMS configuration
        provider = channel_config.get("provider", "").lower()
        api_key = channel_config.get("api_key", "")
        sender = channel_config.get("sender", "")
        recipients = channel_config.get("recipients", [])
        
        if not provider:
            return {
                "status": "error",
                "error": "SMS provider not specified",
            }
        
        if not api_key:
            return {
                "status": "error",
                "error": "SMS API key not specified",
            }
        
        if not recipients:
            return {
                "status": "error",
                "error": "SMS recipients not specified",
            }
        
        try:
            # Send SMS based on provider
            if provider == "twilio":
                return self._send_twilio_sms(
                    api_key=api_key,
                    account_sid=channel_config.get("account_sid", ""),
                    sender=sender,
                    recipients=recipients,
                    message=message,
                )
            elif provider == "nexmo" or provider == "vonage":
                return self._send_vonage_sms(
                    api_key=api_key,
                    api_secret=channel_config.get("api_secret", ""),
                    sender=sender,
                    recipients=recipients,
                    message=message,
                )
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported SMS provider: {provider}",
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def _send_twilio_sms(self, api_key: str, account_sid: str, sender: str,
                        recipients: List[str], message: str) -> Dict:
        """
        Send an SMS using Twilio.
        
        Args:
            api_key: Twilio auth token
            account_sid: Twilio account SID
            sender: Sender phone number
            recipients: Recipient phone numbers
            message: SMS message
            
        Returns:
            Result of sending the SMS
        """
        if not account_sid:
            return {
                "status": "error",
                "error": "Twilio account SID not specified",
            }
        
        try:
            from twilio.rest import Client
            
            # Create Twilio client
            client = Client(account_sid, api_key)
            
            # Send SMS to all recipients
            results = {}
            for recipient in recipients:
                try:
                    sms = client.messages.create(
                        body=message,
                        from_=sender,
                        to=recipient,
                    )
                    results[recipient] = {
                        "status": "ok",
                        "message_sid": sms.sid,
                    }
                except Exception as e:
                    results[recipient] = {
                        "status": "error",
                        "error": str(e),
                    }
            
            # Check if any SMS was sent successfully
            success = any(result.get("status") == "ok" for result in results.values())
            
            if success:
                return {
                    "status": "ok",
                    "results": results,
                }
            else:
                return {
                    "status": "error",
                    "error": "Failed to send SMS to any recipient",
                    "results": results,
                }
        except ImportError:
            return {
                "status": "error",
                "error": "twilio not installed",
            }
    
    def _send_vonage_sms(self, api_key: str, api_secret: str, sender: str,
                        recipients: List[str], message: str) -> Dict:
        """
        Send an SMS using Vonage (formerly Nexmo).
        
        Args:
            api_key: Vonage API key
            api_secret: Vonage API secret
            sender: Sender name or phone number
            recipients: Recipient phone numbers
            message: SMS message
            
        Returns:
            Result of sending the SMS
        """
        if not api_secret:
            return {
                "status": "error",
                "error": "Vonage API secret not specified",
            }
        
        try:
            import vonage
            
            # Create Vonage client
            client = vonage.Client(key=api_key, secret=api_secret)
            sms = vonage.Sms(client)
            
            # Send SMS to all recipients
            results = {}
            for recipient in recipients:
                try:
                    response = sms.send_message({
                        "from": sender,
                        "to": recipient,
                        "text": message,
                    })
                    
                    if response["messages"][0]["status"] == "0":
                        results[recipient] = {
                            "status": "ok",
                            "message_id": response["messages"][0]["message-id"],
                        }
                    else:
                        results[recipient] = {
                            "status": "error",
                            "error": response["messages"][0]["error-text"],
                        }
                except Exception as e:
                    results[recipient] = {
                        "status": "error",
                        "error": str(e),
                    }
            
            # Check if any SMS was sent successfully
            success = any(result.get("status") == "ok" for result in results.values())
            
            if success:
                return {
                    "status": "ok",
                    "results": results,
                }
            else:
                return {
                    "status": "error",
                    "error": "Failed to send SMS to any recipient",
                    "results": results,
                }
        except ImportError:
            return {
                "status": "error",
                "error": "vonage not installed",
            }


def main():
    """Main function for testing the integration module."""
    # Create service integration instance
    integration = ServiceIntegration()
    
    # Register a test HTTP service
    integration.register_service(
        service_name="test_http",
        service_config={
            "type": "http",
            "url": "https://httpbin.org",
            "enabled": True,
        },
    )
    
    # Check service status
    status = integration.check_service("test_http")
    logger.info(f"Service status: {status}")
    
    # Call service method
    result = integration.call_service(
        service_name="test_http",
        method="request",
        url="/get",
        params={"test": "value"},
    )
    logger.info(f"Service call result: {result}")
    
    # Create notification system instance
    notification = NotificationSystem()
    
    # Register a test webhook notification channel
    notification.register_channel(
        channel_name="test_webhook",
        channel_config={
            "type": "webhook",
            "url": "https://httpbin.org/post",
            "method": "POST",
            "include_timestamp": True,
            "enabled": True,
        },
    )
    
    # Send a test notification
    result = notification.send_notification(
        message="This is a test notification",
        channel="test_webhook",
        subject="Test Notification",
    )
    logger.info(f"Notification result: {result}")
    
    logger.info("Integration module test completed successfully")


if __name__ == "__main__":
    main()
