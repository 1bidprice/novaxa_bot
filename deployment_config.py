#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Deployment Configuration Module for Telegram Bot
-----------------------------------------------
Provides configuration management for the Enhanced Telegram Bot deployment.

This module handles configuration settings for different deployment environments,
including local development, staging, and production.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Callable

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class DeploymentConfig:
    """
    Manages deployment configuration for the Telegram bot.
    
    This class provides methods for managing configuration settings
    for different deployment environments.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the deployment configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = {}
        
        # Load configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        else:
            # Set default configuration
            self.config = {
                "environments": {
                    "local": {
                        "name": "Local Development",
                        "description": "Local development environment",
                        "host": "localhost",
                        "port": 8443,
                        "use_webhook": False,
                        "webhook_url": None,
                        "certificate": None,
                        "env_vars": {
                            "DEBUG": "true",
                            "LOG_LEVEL": "DEBUG",
                        },
                        "service_name": None,
                    },
                    "staging": {
                        "name": "Staging",
                        "description": "Staging environment for testing",
                        "host": "staging.example.com",
                        "port": 8443,
                        "use_webhook": True,
                        "webhook_url": "https://staging.example.com/webhook",
                        "certificate": "certs/staging.pem",
                        "env_vars": {
                            "DEBUG": "true",
                            "LOG_LEVEL": "INFO",
                        },
                        "service_name": "telegram-bot-staging",
                    },
                    "production": {
                        "name": "Production",
                        "description": "Production environment",
                        "host": "example.com",
                        "port": 8443,
                        "use_webhook": True,
                        "webhook_url": "https://example.com/webhook",
                        "certificate": "certs/production.pem",
                        "env_vars": {
                            "DEBUG": "false",
                            "LOG_LEVEL": "WARNING",
                        },
                        "service_name": "telegram-bot",
                    },
                },
                "default_environment": "local",
                "bot_settings": {
                    "name": "Enhanced Telegram Bot",
                    "description": "A feature-rich Telegram bot with advanced capabilities",
                    "version": "1.0.0",
                    "author": "Your Name",
                    "license": "MIT",
                    "repository": "https://github.com/yourusername/enhanced-telegram-bot",
                },
                "deployment_settings": {
                    "backup_enabled": True,
                    "backup_count": 5,
                    "auto_restart": True,
                    "health_check_enabled": True,
                    "health_check_interval": 60,
                    "notification_enabled": True,
                    "notification_email": "admin@example.com",
                },
                "render_settings": {
                    "service_name": "enhanced-telegram-bot",
                    "service_type": "web",
                    "plan": "free",
                    "region": "oregon",
                    "branch": "main",
                    "build_command": "pip install -r requirements.txt",
                    "start_command": "python enhanced_bot.py",
                    "env_vars": {
                        "PYTHON_VERSION": "3.9.0",
                    },
                },
            }
        
        logger.info("Deployment configuration manager initialized")
    
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
            
            logger.info(f"Loaded deployment configuration from {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading deployment configuration: {e}")
            return False
    
    def save_config(self, config_file: str = None) -> bool:
        """
        Save configuration to a file.
        
        Args:
            config_file: Path to save configuration file (if None, use the current config file)
            
        Returns:
            True if configuration was saved successfully, False otherwise
        """
        if config_file is None:
            config_file = self.config_file
        
        if not config_file:
            logger.error("No configuration file specified")
            return False
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Saved deployment configuration to {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving deployment configuration: {e}")
            return False
    
    def get_environment(self, env_name: str) -> Dict:
        """
        Get configuration for a specific environment.
        
        Args:
            env_name: Name of the environment
            
        Returns:
            Environment configuration
        """
        environments = self.config.get("environments", {})
        return environments.get(env_name, {})
    
    def get_environments(self) -> Dict:
        """
        Get all environment configurations.
        
        Returns:
            Dictionary of environment configurations
        """
        return self.config.get("environments", {})
    
    def get_default_environment(self) -> str:
        """
        Get the default environment name.
        
        Returns:
            Default environment name
        """
        return self.config.get("default_environment", "local")
    
    def set_default_environment(self, env_name: str) -> bool:
        """
        Set the default environment.
        
        Args:
            env_name: Name of the environment to set as default
            
        Returns:
            True if default environment was set successfully, False otherwise
        """
        if env_name not in self.config.get("environments", {}):
            logger.error(f"Environment not found: {env_name}")
            return False
        
        self.config["default_environment"] = env_name
        logger.info(f"Set default environment to: {env_name}")
        return True
    
    def add_environment(self, env_name: str, env_config: Dict) -> bool:
        """
        Add a new environment.
        
        Args:
            env_name: Name of the environment
            env_config: Configuration for the environment
            
        Returns:
            True if environment was added successfully, False otherwise
        """
        if "environments" not in self.config:
            self.config["environments"] = {}
        
        self.config["environments"][env_name] = env_config
        logger.info(f"Added environment: {env_name}")
        return True
    
    def update_environment(self, env_name: str, env_config: Dict) -> bool:
        """
        Update an existing environment.
        
        Args:
            env_name: Name of the environment
            env_config: New configuration for the environment
            
        Returns:
            True if environment was updated successfully, False otherwise
        """
        if env_name not in self.config.get("environments", {}):
            logger.error(f"Environment not found: {env_name}")
            return False
        
        self.config["environments"][env_name] = env_config
        logger.info(f"Updated environment: {env_name}")
        return True
    
    def remove_environment(self, env_name: str) -> bool:
        """
        Remove an environment.
        
        Args:
            env_name: Name of the environment to remove
            
        Returns:
            True if environment was removed successfully, False otherwise
        """
        if env_name not in self.config.get("environments", {}):
            logger.error(f"Environment not found: {env_name}")
            return False
        
        del self.config["environments"][env_name]
        
        # Update default environment if it was removed
        if self.config.get("default_environment") == env_name:
            if self.config.get("environments"):
                self.config["default_environment"] = next(iter(self.config["environments"].keys()))
            else:
                self.config["default_environment"] = "local"
        
        logger.info(f"Removed environment: {env_name}")
        return True
    
    def get_bot_settings(self) -> Dict:
        """
        Get bot settings.
        
        Returns:
            Bot settings
        """
        return self.config.get("bot_settings", {})
    
    def update_bot_settings(self, settings: Dict) -> bool:
        """
        Update bot settings.
        
        Args:
            settings: New bot settings
            
        Returns:
            True if settings were updated successfully, False otherwise
        """
        if "bot_settings" not in self.config:
            self.config["bot_settings"] = {}
        
        self.config["bot_settings"].update(settings)
        logger.info("Updated bot settings")
        return True
    
    def get_deployment_settings(self) -> Dict:
        """
        Get deployment settings.
        
        Returns:
            Deployment settings
        """
        return self.config.get("deployment_settings", {})
    
    def update_deployment_settings(self, settings: Dict) -> bool:
        """
        Update deployment settings.
        
        Args:
            settings: New deployment settings
            
        Returns:
            True if settings were updated successfully, False otherwise
        """
        if "deployment_settings" not in self.config:
            self.config["deployment_settings"] = {}
        
        self.config["deployment_settings"].update(settings)
        logger.info("Updated deployment settings")
        return True
    
    def get_render_settings(self) -> Dict:
        """
        Get Render platform settings.
        
        Returns:
            Render settings
        """
        return self.config.get("render_settings", {})
    
    def update_render_settings(self, settings: Dict) -> bool:
        """
        Update Render platform settings.
        
        Args:
            settings: New Render settings
            
        Returns:
            True if settings were updated successfully, False otherwise
        """
        if "render_settings" not in self.config:
            self.config["render_settings"] = {}
        
        self.config["render_settings"].update(settings)
        logger.info("Updated Render settings")
        return True
    
    def get_environment_variables(self, env_name: str) -> Dict:
        """
        Get environment variables for a specific environment.
        
        Args:
            env_name: Name of the environment
            
        Returns:
            Environment variables
        """
        env_config = self.get_environment(env_name)
        return env_config.get("env_vars", {})
    
    def update_environment_variables(self, env_name: str, env_vars: Dict) -> bool:
        """
        Update environment variables for a specific environment.
        
        Args:
            env_name: Name of the environment
            env_vars: New environment variables
            
        Returns:
            True if environment variables were updated successfully, False otherwise
        """
        if env_name not in self.config.get("environments", {}):
            logger.error(f"Environment not found: {env_name}")
            return False
        
        if "env_vars" not in self.config["environments"][env_name]:
            self.config["environments"][env_name]["env_vars"] = {}
        
        self.config["environments"][env_name]["env_vars"].update(env_vars)
        logger.info(f"Updated environment variables for {env_name}")
        return True
    
    def generate_env_file(self, env_name: str, output_file: str) -> bool:
        """
        Generate a .env file for a specific environment.
        
        Args:
            env_name: Name of the environment
            output_file: Path to output .env file
            
        Returns:
            True if .env file was generated successfully, False otherwise
        """
        env_vars = self.get_environment_variables(env_name)
        
        if not env_vars:
            logger.warning(f"No environment variables found for {env_name}")
        
        try:
            with open(output_file, 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            logger.info(f"Generated .env file for {env_name} at {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error generating .env file: {e}")
            return False
    
    def generate_render_yaml(self, output_file: str) -> bool:
        """
        Generate a render.yaml file for Render platform deployment.
        
        Args:
            output_file: Path to output render.yaml file
            
        Returns:
            True if render.yaml file was generated successfully, False otherwise
        """
        render_settings = self.get_render_settings()
        
        if not render_settings:
            logger.warning("No Render settings found")
            return False
        
        try:
            # Create render.yaml content
            content = {
                "services": [
                    {
                        "type": render_settings.get("service_type", "web"),
                        "name": render_settings.get("service_name", "enhanced-telegram-bot"),
                        "plan": render_settings.get("plan", "free"),
                        "region": render_settings.get("region", "oregon"),
                        "env": render_settings.get("env", "python"),
                        "buildCommand": render_settings.get("build_command", "pip install -r requirements.txt"),
                        "startCommand": render_settings.get("start_command", "python enhanced_bot.py"),
                        "envVars": [
                            {"key": key, "value": value}
                            for key, value in render_settings.get("env_vars", {}).items()
                        ],
                    }
                ]
            }
            
            # Write to file
            with open(output_file, 'w') as f:
                yaml.dump(content, f, default_flow_style=False)
            
            logger.info(f"Generated render.yaml file at {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error generating render.yaml file: {e}")
            return False
    
    def generate_systemd_service(self, env_name: str, output_file: str) -> bool:
        """
        Generate a systemd service file for a specific environment.
        
        Args:
            env_name: Name of the environment
            output_file: Path to output service file
            
        Returns:
            True if service file was generated successfully, False otherwise
        """
        env_config = self.get_environment(env_name)
        service_name = env_config.get("service_name")
        
        if not service_name:
            logger.warning(f"No service name found for {env_name}")
            return False
        
        try:
            # Create service file content
            content = f"""[Unit]
Description=Enhanced Telegram Bot ({env_name})
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/telegram-bot
ExecStart=/usr/bin/python3 /opt/telegram-bot/enhanced_bot.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier={service_name}
Environment=PYTHONUNBUFFERED=1
"""
            
            # Add environment variables
            for key, value in env_config.get("env_vars", {}).items():
                content += f'Environment="{key}={value}"\n'
            
            content += """
[Install]
WantedBy=multi-user.target
"""
            
            # Write to file
            with open(output_file, 'w') as f:
                f.write(content)
            
            logger.info(f"Generated systemd service file for {env_name} at {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error generating systemd service file: {e}")
            return False


def main():
    """Main function for the deployment configuration module."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Telegram Bot Deployment Configuration Tool")
    parser.add_argument("--config", help="Path to deployment configuration file")
    parser.add_argument("--save", help="Save configuration to a file")
    parser.add_argument("--env-file", help="Generate .env file for an environment")
    parser.add_argument("--env", help="Environment name for operations")
    parser.add_argument("--render-yaml", help="Generate render.yaml file")
    parser.add_argument("--systemd-service", help="Generate systemd service file")
    parser.add_argument("--list-env", action="store_true", help="List available environments")
    
    args = parser.parse_args()
    
    # Create deployment configuration manager
    config_manager = DeploymentConfig(config_file=args.config)
    
    if args.list_env:
        # List available environments
        environments = config_manager.get_environments()
        default_env = config_manager.get_default_environment()
        
        print("Available environments:")
        for env_name, env_config in environments.items():
            default_marker = " (default)" if env_name == default_env else ""
            print(f"  {env_name}{default_marker}: {env_config.get('name', env_name)} - {env_config.get('description', '')}")
        return
    
    if args.env_file:
        # Generate .env file
        env_name = args.env or config_manager.get_default_environment()
        result = config_manager.generate_env_file(env_name, args.env_file)
        
        if result:
            print(f"Generated .env file for {env_name} at {args.env_file}")
        else:
            print(f"Failed to generate .env file for {env_name}")
        return
    
    if args.render_yaml:
        # Generate render.yaml file
        result = config_manager.generate_render_yaml(args.render_yaml)
        
        if result:
            print(f"Generated render.yaml file at {args.render_yaml}")
        else:
            print("Failed to generate render.yaml file")
        return
    
    if args.systemd_service:
        # Generate systemd service file
        env_name = args.env or config_manager.get_default_environment()
        result = config_manager.generate_systemd_service(env_name, args.systemd_service)
        
        if result:
            print(f"Generated systemd service file for {env_name} at {args.systemd_service}")
        else:
            print(f"Failed to generate systemd service file for {env_name}")
        return
    
    if args.save:
        # Save configuration to a file
        result = config_manager.save_config(args.save)
        
        if result:
            print(f"Saved deployment configuration to {args.save}")
        else:
            print(f"Failed to save deployment configuration to {args.save}")
        return
    
    # If no specific action was requested, print help
    parser.print_help()


if __name__ == "__main__":
    main()
