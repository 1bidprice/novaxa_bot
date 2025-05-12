#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Deployment Module for Telegram Bot
----------------------------------
Provides deployment functionality for the Enhanced Telegram Bot.

This module handles deployment of the bot to various environments,
including local, staging, and production.
"""

import os
import sys
import logging
import json
import time
import shutil
import subprocess
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class Deployment:
    """
    Handles deployment of the Telegram bot.
    
    This class provides methods for deploying the bot to different environments,
    managing configurations, and handling deployment-related tasks.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the deployment handler.
        
        Args:
            config_file: Path to deployment configuration file
        """
        self.config = {}
        self.environments = {}
        self.current_environment = None
        
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
                    },
                },
                "default_environment": "local",
                "deployment_history": [],
            }
            
            # Initialize environments
            self.environments = self.config["environments"]
            self.current_environment = self.config["default_environment"]
        
        logger.info("Deployment handler initialized")
    
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
            
            # Initialize environments
            self.environments = self.config.get("environments", {})
            self.current_environment = self.config.get("default_environment", "local")
            
            logger.info(f"Loaded deployment configuration from {config_file}")
            logger.info(f"Available environments: {', '.join(self.environments.keys())}")
            logger.info(f"Current environment: {self.current_environment}")
            return True
        except Exception as e:
            logger.error(f"Error loading deployment configuration: {e}")
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
            
            logger.info(f"Saved deployment configuration to {config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving deployment configuration: {e}")
            return False
    
    def add_environment(self, env_name: str, env_config: Dict) -> bool:
        """
        Add a new environment.
        
        Args:
            env_name: Name of the environment
            env_config: Configuration for the environment
            
        Returns:
            True if environment was added successfully, False otherwise
        """
        try:
            # Add environment to configuration
            if "environments" not in self.config:
                self.config["environments"] = {}
            
            self.config["environments"][env_name] = env_config
            self.environments = self.config["environments"]
            
            logger.info(f"Added environment: {env_name}")
            return True
        except Exception as e:
            logger.error(f"Error adding environment: {e}")
            return False
    
    def remove_environment(self, env_name: str) -> bool:
        """
        Remove an environment.
        
        Args:
            env_name: Name of the environment to remove
            
        Returns:
            True if environment was removed successfully, False otherwise
        """
        if env_name not in self.environments:
            logger.error(f"Environment not found: {env_name}")
            return False
        
        try:
            # Remove environment from configuration
            del self.config["environments"][env_name]
            self.environments = self.config["environments"]
            
            # Update current environment if it was removed
            if self.current_environment == env_name:
                self.current_environment = self.config.get("default_environment", "local")
                if self.current_environment not in self.environments:
                    self.current_environment = next(iter(self.environments.keys())) if self.environments else None
            
            logger.info(f"Removed environment: {env_name}")
            return True
        except Exception as e:
            logger.error(f"Error removing environment: {e}")
            return False
    
    def set_current_environment(self, env_name: str) -> bool:
        """
        Set the current environment.
        
        Args:
            env_name: Name of the environment to set as current
            
        Returns:
            True if environment was set successfully, False otherwise
        """
        if env_name not in self.environments:
            logger.error(f"Environment not found: {env_name}")
            return False
        
        try:
            self.current_environment = env_name
            logger.info(f"Set current environment to: {env_name}")
            return True
        except Exception as e:
            logger.error(f"Error setting current environment: {e}")
            return False
    
    def get_environment_config(self, env_name: str = None) -> Dict:
        """
        Get configuration for an environment.
        
        Args:
            env_name: Name of the environment (if None, use current environment)
            
        Returns:
            Environment configuration
        """
        if env_name is None:
            env_name = self.current_environment
        
        if env_name not in self.environments:
            logger.error(f"Environment not found: {env_name}")
            return {}
        
        return self.environments[env_name].copy()
    
    def deploy(self, env_name: str = None, source_dir: str = None, options: Dict = None) -> Dict:
        """
        Deploy the bot to an environment.
        
        Args:
            env_name: Name of the environment to deploy to (if None, use current environment)
            source_dir: Source directory containing the bot code (if None, use current directory)
            options: Additional deployment options
            
        Returns:
            Deployment result
        """
        if env_name is None:
            env_name = self.current_environment
        
        if env_name not in self.environments:
            return {
                "status": "error",
                "error": f"Environment not found: {env_name}",
            }
        
        if source_dir is None:
            source_dir = os.getcwd()
        
        if not os.path.isdir(source_dir):
            return {
                "status": "error",
                "error": f"Source directory not found: {source_dir}",
            }
        
        if options is None:
            options = {}
        
        # Get environment configuration
        env_config = self.environments[env_name]
        
        # Start deployment
        deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        deployment_start_time = datetime.now()
        
        logger.info(f"Starting deployment {deployment_id} to environment: {env_name}")
        
        try:
            # Prepare deployment
            result = self._prepare_deployment(env_name, source_dir, options)
            if result.get("status") != "ok":
                return result
            
            # Execute deployment
            result = self._execute_deployment(env_name, source_dir, options)
            if result.get("status") != "ok":
                return result
            
            # Verify deployment
            result = self._verify_deployment(env_name, options)
            if result.get("status") != "ok":
                return result
            
            # Record deployment
            deployment_end_time = datetime.now()
            deployment_duration = (deployment_end_time - deployment_start_time).total_seconds()
            
            deployment_record = {
                "id": deployment_id,
                "environment": env_name,
                "start_time": deployment_start_time.isoformat(),
                "end_time": deployment_end_time.isoformat(),
                "duration": deployment_duration,
                "status": "success",
                "options": options,
            }
            
            if "deployment_history" not in self.config:
                self.config["deployment_history"] = []
            
            self.config["deployment_history"].append(deployment_record)
            
            logger.info(f"Deployment {deployment_id} completed successfully in {deployment_duration:.2f} seconds")
            
            return {
                "status": "ok",
                "deployment_id": deployment_id,
                "environment": env_name,
                "start_time": deployment_start_time.isoformat(),
                "end_time": deployment_end_time.isoformat(),
                "duration": deployment_duration,
                "message": f"Deployment to {env_name} completed successfully",
            }
        except Exception as e:
            # Record failed deployment
            deployment_end_time = datetime.now()
            deployment_duration = (deployment_end_time - deployment_start_time).total_seconds()
            
            deployment_record = {
                "id": deployment_id,
                "environment": env_name,
                "start_time": deployment_start_time.isoformat(),
                "end_time": deployment_end_time.isoformat(),
                "duration": deployment_duration,
                "status": "error",
                "error": str(e),
                "options": options,
            }
            
            if "deployment_history" not in self.config:
                self.config["deployment_history"] = []
            
            self.config["deployment_history"].append(deployment_record)
            
            logger.error(f"Deployment {deployment_id} failed: {e}")
            
            return {
                "status": "error",
                "deployment_id": deployment_id,
                "environment": env_name,
                "start_time": deployment_start_time.isoformat(),
                "end_time": deployment_end_time.isoformat(),
                "duration": deployment_duration,
                "error": str(e),
            }
    
    def _prepare_deployment(self, env_name: str, source_dir: str, options: Dict) -> Dict:
        """
        Prepare for deployment.
        
        Args:
            env_name: Name of the environment
            source_dir: Source directory
            options: Deployment options
            
        Returns:
            Preparation result
        """
        logger.info(f"Preparing deployment to {env_name}")
        
        # Get environment configuration
        env_config = self.environments[env_name]
        
        # Validate source directory
        required_files = ["enhanced_bot.py", "api.py", "integration.py", "monitor.py"]
        missing_files = [file for file in required_files if not os.path.exists(os.path.join(source_dir, file))]
        
        if missing_files:
            return {
                "status": "error",
                "error": f"Missing required files: {', '.join(missing_files)}",
            }
        
        # Create deployment directory if needed
        deploy_dir = options.get("deploy_dir")
        if deploy_dir:
            os.makedirs(deploy_dir, exist_ok=True)
        
        return {
            "status": "ok",
            "message": "Deployment preparation completed",
        }
    
    def _execute_deployment(self, env_name: str, source_dir: str, options: Dict) -> Dict:
        """
        Execute deployment.
        
        Args:
            env_name: Name of the environment
            source_dir: Source directory
            options: Deployment options
            
        Returns:
            Execution result
        """
        logger.info(f"Executing deployment to {env_name}")
        
        # Get environment configuration
        env_config = self.environments[env_name]
        
        # Get deployment options
        deploy_dir = options.get("deploy_dir")
        backup = options.get("backup", True)
        restart = options.get("restart", True)
        
        # Copy files to deployment directory if specified
        if deploy_dir:
            # Create backup if enabled
            if backup and os.path.exists(deploy_dir):
                backup_dir = f"{deploy_dir}_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                shutil.copytree(deploy_dir, backup_dir)
                logger.info(f"Created backup at {backup_dir}")
            
            # Copy files
            for item in os.listdir(source_dir):
                source_item = os.path.join(source_dir, item)
                dest_item = os.path.join(deploy_dir, item)
                
                if os.path.isdir(source_item):
                    if os.path.exists(dest_item):
                        shutil.rmtree(dest_item)
                    shutil.copytree(source_item, dest_item)
                else:
                    shutil.copy2(source_item, dest_item)
            
            logger.info(f"Copied files to {deploy_dir}")
        
        # Create environment file
        env_vars = env_config.get("env_vars", {})
        env_file_path = os.path.join(deploy_dir or source_dir, ".env")
        
        with open(env_file_path, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        logger.info(f"Created environment file at {env_file_path}")
        
        # Restart service if enabled
        if restart:
            self._restart_service(env_name, deploy_dir or source_dir, options)
        
        return {
            "status": "ok",
            "message": "Deployment execution completed",
        }
    
    def _restart_service(self, env_name: str, deploy_dir: str, options: Dict) -> Dict:
        """
        Restart the bot service.
        
        Args:
            env_name: Name of the environment
            deploy_dir: Deployment directory
            options: Deployment options
            
        Returns:
            Restart result
        """
        logger.info(f"Restarting service in {env_name}")
        
        # Get environment configuration
        env_config = self.environments[env_name]
        
        # Check if systemd service is specified
        service_name = options.get("service_name") or env_config.get("service_name")
        
        if service_name:
            try:
                # Restart systemd service
                subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)
                logger.info(f"Restarted systemd service: {service_name}")
                return {
                    "status": "ok",
                    "message": f"Restarted service: {service_name}",
                }
            except subprocess.CalledProcessError as e:
                logger.error(f"Error restarting systemd service: {e}")
                return {
                    "status": "error",
                    "error": f"Error restarting systemd service: {e}",
                }
        else:
            # No service specified, just log a message
            logger.info("No service specified for restart")
            return {
                "status": "ok",
                "message": "No service specified for restart",
            }
    
    def _verify_deployment(self, env_name: str, options: Dict) -> Dict:
        """
        Verify deployment.
        
        Args:
            env_name: Name of the environment
            options: Deployment options
            
        Returns:
            Verification result
        """
        logger.info(f"Verifying deployment to {env_name}")
        
        # Get environment configuration
        env_config = self.environments[env_name]
        
        # Get verification options
        verify_timeout = options.get("verify_timeout", 30)
        
        # Check if webhook URL is specified
        webhook_url = env_config.get("webhook_url")
        
        if webhook_url:
            try:
                # Check webhook URL
                response = requests.get(webhook_url, timeout=verify_timeout)
                
                if response.status_code == 200:
                    logger.info(f"Webhook URL is accessible: {webhook_url}")
                    return {
                        "status": "ok",
                        "message": "Deployment verification completed",
                    }
                else:
                    logger.warning(f"Webhook URL returned status code {response.status_code}: {webhook_url}")
                    return {
                        "status": "warning",
                        "message": f"Webhook URL returned status code {response.status_code}",
                    }
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error accessing webhook URL: {e}")
                return {
                    "status": "warning",
                    "message": f"Error accessing webhook URL: {e}",
                }
        
        # No webhook URL specified, just log a message
        logger.info("No webhook URL specified for verification")
        return {
            "status": "ok",
            "message": "Deployment verification completed",
        }
    
    def get_deployment_history(self, count: int = 10, env_name: str = None) -> List[Dict]:
        """
        Get deployment history.
        
        Args:
            count: Number of deployments to retrieve
            env_name: Filter by environment name
            
        Returns:
            List of deployment records
        """
        history = self.config.get("deployment_history", [])
        
        # Filter by environment if specified
        if env_name:
            history = [record for record in history if record.get("environment") == env_name]
        
        # Sort by start time (newest first)
        history = sorted(history, key=lambda x: x.get("start_time", ""), reverse=True)
        
        # Return limited number of records
        return history[:count]
    
    def rollback(self, deployment_id: str = None) -> Dict:
        """
        Rollback to a previous deployment.
        
        Args:
            deployment_id: ID of the deployment to rollback to (if None, rollback to the previous successful deployment)
            
        Returns:
            Rollback result
        """
        history = self.config.get("deployment_history", [])
        
        if not history:
            return {
                "status": "error",
                "error": "No deployment history available",
            }
        
        # Sort by start time (newest first)
        history = sorted(history, key=lambda x: x.get("start_time", ""), reverse=True)
        
        # Find deployment to rollback to
        target_deployment = None
        
        if deployment_id:
            # Find specific deployment
            for record in history:
                if record.get("id") == deployment_id:
                    target_deployment = record
                    break
            
            if not target_deployment:
                return {
                    "status": "error",
                    "error": f"Deployment not found: {deployment_id}",
                }
        else:
            # Find previous successful deployment
            current_env = self.current_environment
            
            # Skip the most recent deployment (which is the one we want to rollback from)
            for record in history[1:]:
                if record.get("environment") == current_env and record.get("status") == "success":
                    target_deployment = record
                    break
            
            if not target_deployment:
                return {
                    "status": "error",
                    "error": f"No previous successful deployment found for environment: {current_env}",
                }
        
        # Get deployment details
        env_name = target_deployment.get("environment")
        options = target_deployment.get("options", {})
        
        # Check if backup exists
        deploy_dir = options.get("deploy_dir")
        if not deploy_dir:
            return {
                "status": "error",
                "error": "Deployment directory not specified in the target deployment",
            }
        
        backup_dir = f"{deploy_dir}_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Start rollback
        rollback_id = f"rollback_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        rollback_start_time = datetime.now()
        
        logger.info(f"Starting rollback {rollback_id} to deployment: {deployment_id or 'previous'}")
        
        try:
            # Create backup of current deployment
            if os.path.exists(deploy_dir):
                shutil.copytree(deploy_dir, backup_dir)
                logger.info(f"Created backup at {backup_dir}")
            
            # Find backup directory for target deployment
            target_backup_dir = None
            target_time = datetime.fromisoformat(target_deployment.get("end_time", ""))
            
            for item in os.listdir(os.path.dirname(deploy_dir)):
                if item.startswith(f"{os.path.basename(deploy_dir)}_backup_"):
                    try:
                        # Extract timestamp from backup directory name
                        timestamp_str = item.split("_backup_")[1]
                        timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
                        
                        # Check if this backup is from the target deployment
                        if timestamp <= target_time:
                            if target_backup_dir is None or timestamp > datetime.strptime(target_backup_dir.split("_backup_")[1], "%Y%m%d%H%M%S"):
                                target_backup_dir = os.path.join(os.path.dirname(deploy_dir), item)
                    except (ValueError, IndexError):
                        continue
            
            if not target_backup_dir:
                return {
                    "status": "error",
                    "error": "Backup directory for target deployment not found",
                }
            
            # Restore from backup
            if os.path.exists(deploy_dir):
                shutil.rmtree(deploy_dir)
            
            shutil.copytree(target_backup_dir, deploy_dir)
            logger.info(f"Restored from backup: {target_backup_dir}")
            
            # Restart service
            restart_result = self._restart_service(env_name, deploy_dir, options)
            
            # Record rollback
            rollback_end_time = datetime.now()
            rollback_duration = (rollback_end_time - rollback_start_time).total_seconds()
            
            rollback_record = {
                "id": rollback_id,
                "environment": env_name,
                "target_deployment": target_deployment.get("id"),
                "start_time": rollback_start_time.isoformat(),
                "end_time": rollback_end_time.isoformat(),
                "duration": rollback_duration,
                "status": "success",
                "options": options,
            }
            
            if "rollback_history" not in self.config:
                self.config["rollback_history"] = []
            
            self.config["rollback_history"].append(rollback_record)
            
            logger.info(f"Rollback {rollback_id} completed successfully in {rollback_duration:.2f} seconds")
            
            return {
                "status": "ok",
                "rollback_id": rollback_id,
                "environment": env_name,
                "target_deployment": target_deployment.get("id"),
                "start_time": rollback_start_time.isoformat(),
                "end_time": rollback_end_time.isoformat(),
                "duration": rollback_duration,
                "message": f"Rollback to deployment {target_deployment.get('id')} completed successfully",
            }
        except Exception as e:
            # Record failed rollback
            rollback_end_time = datetime.now()
            rollback_duration = (rollback_end_time - rollback_start_time).total_seconds()
            
            rollback_record = {
                "id": rollback_id,
                "environment": env_name,
                "target_deployment": target_deployment.get("id"),
                "start_time": rollback_start_time.isoformat(),
                "end_time": rollback_end_time.isoformat(),
                "duration": rollback_duration,
                "status": "error",
                "error": str(e),
                "options": options,
            }
            
            if "rollback_history" not in self.config:
                self.config["rollback_history"] = []
            
            self.config["rollback_history"].append(rollback_record)
            
            logger.error(f"Rollback {rollback_id} failed: {e}")
            
            return {
                "status": "error",
                "rollback_id": rollback_id,
                "environment": env_name,
                "target_deployment": target_deployment.get("id"),
                "start_time": rollback_start_time.isoformat(),
                "end_time": rollback_end_time.isoformat(),
                "duration": rollback_duration,
                "error": str(e),
            }


def main():
    """Main function for the deployment module."""
    parser = argparse.ArgumentParser(description="Telegram Bot Deployment Tool")
    parser.add_argument("--config", help="Path to deployment configuration file")
    parser.add_argument("--env", help="Environment to deploy to")
    parser.add_argument("--source", help="Source directory containing the bot code")
    parser.add_argument("--deploy-dir", help="Deployment directory")
    parser.add_argument("--backup", action="store_true", help="Create backup before deployment")
    parser.add_argument("--no-restart", action="store_true", help="Skip service restart")
    parser.add_argument("--rollback", help="Rollback to a specific deployment ID")
    parser.add_argument("--list", action="store_true", help="List deployment history")
    parser.add_argument("--list-env", action="store_true", help="List available environments")
    
    args = parser.parse_args()
    
    # Create deployment handler
    deployment = Deployment(config_file=args.config)
    
    if args.list_env:
        # List available environments
        print("Available environments:")
        for env_name, env_config in deployment.environments.items():
            print(f"  {env_name}: {env_config.get('name', env_name)} - {env_config.get('description', '')}")
        print(f"Current environment: {deployment.current_environment}")
        return
    
    if args.list:
        # List deployment history
        history = deployment.get_deployment_history(count=10, env_name=args.env)
        
        if not history:
            print("No deployment history available")
            return
        
        print("Deployment history:")
        for record in history:
            status = record.get("status", "unknown")
            status_str = "✅" if status == "success" else "❌"
            print(f"  {status_str} {record.get('id')}: {record.get('environment')} - {record.get('start_time')}")
        return
    
    if args.rollback:
        # Rollback to a specific deployment
        result = deployment.rollback(deployment_id=args.rollback)
        
        if result.get("status") == "ok":
            print(f"Rollback completed successfully: {result.get('message')}")
        else:
            print(f"Rollback failed: {result.get('error')}")
        return
    
    # Deploy to environment
    env_name = args.env or deployment.current_environment
    source_dir = args.source or os.getcwd()
    
    options = {
        "deploy_dir": args.deploy_dir,
        "backup": args.backup,
        "restart": not args.no_restart,
    }
    
    result = deployment.deploy(env_name=env_name, source_dir=source_dir, options=options)
    
    if result.get("status") == "ok":
        print(f"Deployment completed successfully: {result.get('message')}")
    else:
        print(f"Deployment failed: {result.get('error')}")


if __name__ == "__main__":
    main()
