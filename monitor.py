#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitoring Module for Telegram Bot
----------------------------------
Provides system monitoring and performance tracking for the Enhanced Telegram Bot.

This module handles monitoring of system resources, bot performance,
and user activity tracking.
"""

import os
import sys
import logging
import json
import time
import psutil
import threading
import socket
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class SystemMonitor:
    """
    Monitors system resources and bot status.
    
    This class provides methods for monitoring system resources,
    bot status, and logging system events.
    """
    
    def __init__(self, log_file: str = None, max_log_size: int = 10485760):
        """
        Initialize the system monitor.
        
        Args:
            log_file: Path to log file (if None, logs are kept in memory only)
            max_log_size: Maximum log file size in bytes (default: 10MB)
        """
        self.start_time = datetime.now()
        self.log_file = log_file
        self.max_log_size = max_log_size
        self.logs = deque(maxlen=1000)  # Keep last 1000 logs in memory
        self.user_activity = defaultdict(list)
        self.error_count = 0
        self.warning_count = 0
        self.maintenance_mode = False
        self.system_settings = {
            "max_connections": 100,
            "timeout": 30,
            "rate_limit": 60,
            "maintenance_mode": False,
        }
        
        # Start monitoring thread
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("System monitor initialized")
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        self.monitoring_active = False
        if hasattr(self, 'monitoring_thread') and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1.0)
    
    def _monitoring_loop(self):
        """Background thread for continuous monitoring."""
        while self.monitoring_active:
            try:
                # Log system stats every minute
                self._log_system_stats()
                
                # Sleep for 60 seconds
                for _ in range(60):
                    if not self.monitoring_active:
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Sleep and retry
    
    def _log_system_stats(self):
        """Log current system statistics."""
        try:
            # Get system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Create stats log entry
            stats = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 * 1024 * 1024),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "active_users_24h": len(self._get_active_users_in_period(hours=24)),
            }
            
            # Log at debug level
            logger.debug(f"System stats: {json.dumps(stats)}")
            
            # Add to internal logs
            self._add_log("STATS", "System statistics collected", extra=stats)
        except Exception as e:
            logger.error(f"Error logging system stats: {e}")
    
    def _add_log(self, level: str, message: str, user_id: int = None, extra: Dict = None):
        """
        Add a log entry.
        
        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            message: Log message
            user_id: User ID associated with the log (if applicable)
            extra: Additional data to include in the log
        """
        timestamp = datetime.now()
        
        # Create log entry
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "level": level,
            "message": message,
        }
        
        if user_id is not None:
            log_entry["user_id"] = user_id
        
        if extra is not None:
            log_entry["extra"] = extra
        
        # Add to in-memory logs
        self.logs.append(log_entry)
        
        # Write to log file if configured
        if self.log_file:
            try:
                # Check if log file needs rotation
                if os.path.exists(self.log_file) and os.path.getsize(self.log_file) > self.max_log_size:
                    self._rotate_log_file()
                
                # Append to log file
                with open(self.log_file, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
            except Exception as e:
                logger.error(f"Error writing to log file: {e}")
    
    def _rotate_log_file(self):
        """Rotate the log file when it gets too large."""
        try:
            # Rename current log file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_file = f"{self.log_file}.{timestamp}"
            
            if os.path.exists(self.log_file):
                os.rename(self.log_file, backup_file)
                logger.info(f"Rotated log file to {backup_file}")
        except Exception as e:
            logger.error(f"Error rotating log file: {e}")
    
    def log_activity(self, user_id: int, activity: str, is_admin: bool = False):
        """
        Log user activity.
        
        Args:
            user_id: User ID
            activity: Activity description
            is_admin: Whether the activity was performed by an admin
        """
        timestamp = datetime.now()
        
        # Add to user activity tracking
        self.user_activity[user_id].append({
            "timestamp": timestamp.isoformat(),
            "activity": activity,
            "is_admin": is_admin,
        })
        
        # Trim user activity list if it gets too long
        if len(self.user_activity[user_id]) > 100:
            self.user_activity[user_id] = self.user_activity[user_id][-100:]
        
        # Add to logs
        self._add_log(
            level="INFO",
            message=f"User activity: {activity}",
            user_id=user_id,
            extra={"is_admin": is_admin},
        )
    
    def log_error(self, error_message: str, user_id: int = None, extra: Dict = None):
        """
        Log an error.
        
        Args:
            error_message: Error message
            user_id: User ID associated with the error (if applicable)
            extra: Additional data to include in the log
        """
        self.error_count += 1
        
        # Add to logs
        self._add_log(
            level="ERROR",
            message=error_message,
            user_id=user_id,
            extra=extra,
        )
    
    def log_warning(self, warning_message: str, user_id: int = None, extra: Dict = None):
        """
        Log a warning.
        
        Args:
            warning_message: Warning message
            user_id: User ID associated with the warning (if applicable)
            extra: Additional data to include in the log
        """
        self.warning_count += 1
        
        # Add to logs
        self._add_log(
            level="WARNING",
            message=warning_message,
            user_id=user_id,
            extra=extra,
        )
    
    def get_system_status(self) -> Dict:
        """
        Get current system status.
        
        Returns:
            System status information
        """
        uptime = datetime.now() - self.start_time
        uptime_str = self._format_timedelta(uptime)
        
        # Get current resource usage
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Determine status based on resource usage
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            status = "critical"
        elif cpu_percent > 70 or memory.percent > 70 or disk.percent > 70:
            status = "warning"
        else:
            status = "normal"
        
        # Override status if in maintenance mode
        if self.maintenance_mode:
            status = "maintenance"
        
        # Get active users in the last 24 hours
        active_users = len(self._get_active_users_in_period(hours=24))
        
        return {
            "status": status,
            "uptime": uptime_str,
            "active_users": active_users,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "maintenance_mode": self.maintenance_mode,
        }
    
    def get_usage_statistics(self) -> Dict:
        """
        Get usage statistics.
        
        Returns:
            Usage statistics
        """
        # Get active users in different time periods
        active_users_24h = self._get_active_users_in_period(hours=24)
        active_users_7d = self._get_active_users_in_period(days=7)
        active_users_30d = self._get_active_users_in_period(days=30)
        
        # Get new users in the last 7 days
        new_users_7d = self._get_new_users_in_period(days=7)
        
        # Count total commands
        total_commands = 0
        command_counts = defaultdict(int)
        
        for user_id, activities in self.user_activity.items():
            for activity in activities:
                if activity["activity"].endswith("_command"):
                    total_commands += 1
                    command = activity["activity"].replace("_command", "")
                    command_counts[command] += 1
        
        # Get most popular commands
        popular_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        popular_commands = [cmd for cmd, _ in popular_commands]
        
        # Determine peak usage time
        hour_counts = defaultdict(int)
        for user_id, activities in self.user_activity.items():
            for activity in activities:
                timestamp = datetime.fromisoformat(activity["timestamp"])
                hour_counts[timestamp.hour] += 1
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0] if hour_counts else 0
        peak_usage_time = f"{peak_hour:02d}:00 - {(peak_hour + 1) % 24:02d}:00 UTC"
        
        # Calculate average response time (placeholder)
        avg_response_time = 150  # milliseconds
        
        return {
            "total_users": len(self.user_activity),
            "active_users_24h": len(active_users_24h),
            "active_users_7d": len(active_users_7d),
            "active_users_30d": len(active_users_30d),
            "new_users_7d": len(new_users_7d),
            "total_commands": total_commands,
            "popular_commands": popular_commands,
            "peak_usage_time": peak_usage_time,
            "avg_response_time": avg_response_time,
        }
    
    def get_user_statistics(self) -> Dict:
        """
        Get user statistics.
        
        Returns:
            User statistics
        """
        # Get active users in different time periods
        active_users_24h = self._get_active_users_in_period(hours=24)
        
        # Count activities per user
        user_activity_counts = {}
        for user_id, activities in self.user_activity.items():
            user_activity_counts[user_id] = len(activities)
        
        # Get top users by activity
        top_users = sorted(user_activity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Format top users for display
        top_users_formatted = ""
        for i, (user_id, count) in enumerate(top_users, 1):
            top_users_formatted += f"{i}. User {user_id}: {count} activities\n"
        
        # Get new users in the last 24 hours
        new_users_24h = self._get_new_users_in_period(hours=24)
        
        return {
            "total_users": len(self.user_activity),
            "active_users": len(active_users_24h),
            "new_users_24h": len(new_users_24h),
            "top_users": top_users,
            "top_users_formatted": top_users_formatted,
        }
    
    def get_system_settings(self) -> Dict:
        """
        Get system settings.
        
        Returns:
            System settings
        """
        return self.system_settings.copy()
    
    def update_system_settings(self, settings: Dict) -> bool:
        """
        Update system settings.
        
        Args:
            settings: New settings to apply
            
        Returns:
            True if settings were updated successfully, False otherwise
        """
        try:
            # Update settings
            for key, value in settings.items():
                if key in self.system_settings:
                    self.system_settings[key] = value
            
            # Update maintenance mode flag
            self.maintenance_mode = self.system_settings.get("maintenance_mode", False)
            
            # Log settings update
            self._add_log(
                level="INFO",
                message="System settings updated",
                extra={"settings": settings},
            )
            
            return True
        except Exception as e:
            logger.error(f"Error updating system settings: {e}")
            return False
    
    def toggle_maintenance_mode(self) -> bool:
        """
        Toggle maintenance mode.
        
        Returns:
            New maintenance mode state
        """
        self.maintenance_mode = not self.maintenance_mode
        self.system_settings["maintenance_mode"] = self.maintenance_mode
        
        # Log maintenance mode change
        self._add_log(
            level="INFO",
            message=f"Maintenance mode {'enabled' if self.maintenance_mode else 'disabled'}",
        )
        
        return self.maintenance_mode
    
    def get_recent_logs(self, count: int = 10, level: str = None, user_id: int = None) -> List[Dict]:
        """
        Get recent logs.
        
        Args:
            count: Number of logs to retrieve
            level: Filter logs by level (if specified)
            user_id: Filter logs by user ID (if specified)
            
        Returns:
            List of log entries
        """
        # Filter logs
        filtered_logs = list(self.logs)
        
        if level:
            filtered_logs = [log for log in filtered_logs if log.get("level") == level]
        
        if user_id is not None:
            filtered_logs = [log for log in filtered_logs if log.get("user_id") == user_id]
        
        # Return most recent logs
        return list(reversed(filtered_logs))[:count]
    
    def _get_active_users_in_period(self, hours: int = None, days: int = None) -> List[int]:
        """
        Get users active within the specified time period.
        
        Args:
            hours: Number of hours to look back
            days: Number of days to look back
            
        Returns:
            List of active user IDs
        """
        if hours is None and days is None:
            hours = 24  # Default to 24 hours
        
        # Calculate cutoff time
        if days is not None:
            cutoff_time = datetime.now() - timedelta(days=days)
        else:
            cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Find active users
        active_users = set()
        for user_id, activities in self.user_activity.items():
            for activity in activities:
                activity_time = datetime.fromisoformat(activity["timestamp"])
                if activity_time >= cutoff_time:
                    active_users.add(user_id)
                    break
        
        return list(active_users)
    
    def _get_new_users_in_period(self, hours: int = None, days: int = None) -> List[int]:
        """
        Get new users within the specified time period.
        
        Args:
            hours: Number of hours to look back
            days: Number of days to look back
            
        Returns:
            List of new user IDs
        """
        if hours is None and days is None:
            hours = 24  # Default to 24 hours
        
        # Calculate cutoff time
        if days is not None:
            cutoff_time = datetime.now() - timedelta(days=days)
        else:
            cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Find new users (users whose first activity is after the cutoff time)
        new_users = []
        for user_id, activities in self.user_activity.items():
            if activities:
                first_activity_time = datetime.fromisoformat(activities[0]["timestamp"])
                if first_activity_time >= cutoff_time:
                    new_users.append(user_id)
        
        return new_users
    
    def _format_timedelta(self, td: timedelta) -> str:
        """
        Format a timedelta object as a human-readable string.
        
        Args:
            td: Timedelta object
            
        Returns:
            Formatted string
        """
        total_seconds = int(td.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


class PerformanceTracker:
    """
    Tracks performance metrics for the bot.
    
    This class provides methods for tracking and analyzing
    performance metrics such as response time and resource usage.
    """
    
    def __init__(self, max_samples: int = 1000):
        """
        Initialize the performance tracker.
        
        Args:
            max_samples: Maximum number of samples to keep for each metric
        """
        self.max_samples = max_samples
        self.metrics = {
            "response_time": deque(maxlen=max_samples),
            "cpu_usage": deque(maxlen=max_samples),
            "memory_usage": deque(maxlen=max_samples),
            "api_calls": deque(maxlen=max_samples),
        }
        self.start_time = datetime.now()
        self.last_update = datetime.now()
        
        # Start background thread for periodic updates
        self.update_active = True
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        logger.info("Performance tracker initialized")
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        self.update_active = False
        if hasattr(self, 'update_thread') and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
    
    def _update_loop(self):
        """Background thread for periodic metric updates."""
        while self.update_active:
            try:
                # Update CPU and memory usage
                self.track_cpu_usage()
                self.track_memory_usage()
                
                # Sleep for 5 seconds
                for _ in range(5):
                    if not self.update_active:
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Error in performance update loop: {e}")
                time.sleep(5)  # Sleep and retry
    
    def track_response_time(self, start_time: float, end_time: float = None):
        """
        Track response time for an operation.
        
        Args:
            start_time: Start time (as returned by time.time())
            end_time: End time (if None, current time is used)
        """
        if end_time is None:
            end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        self.metrics["response_time"].append({
            "timestamp": datetime.now().isoformat(),
            "value": response_time,
        })
    
    def track_cpu_usage(self):
        """Track CPU usage."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        self.metrics["cpu_usage"].append({
            "timestamp": datetime.now().isoformat(),
            "value": cpu_percent,
        })
    
    def track_memory_usage(self):
        """Track memory usage."""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
        
        self.metrics["memory_usage"].append({
            "timestamp": datetime.now().isoformat(),
            "value": memory_mb,
        })
    
    def track_api_call(self, api_name: str, success: bool, response_time: float):
        """
        Track an API call.
        
        Args:
            api_name: Name of the API
            success: Whether the call was successful
            response_time: Response time in milliseconds
        """
        self.metrics["api_calls"].append({
            "timestamp": datetime.now().isoformat(),
            "api_name": api_name,
            "success": success,
            "response_time": response_time,
        })
    
    def get_metrics(self) -> Dict:
        """
        Get current performance metrics.
        
        Returns:
            Performance metrics
        """
        # Calculate average response time
        response_times = [m["value"] for m in self.metrics["response_time"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Get latest CPU usage
        cpu_usage = self.metrics["cpu_usage"][-1]["value"] if self.metrics["cpu_usage"] else 0
        
        # Get latest memory usage
        memory_usage = self.metrics["memory_usage"][-1]["value"] if self.metrics["memory_usage"] else 0
        
        # Calculate API success rate
        api_calls = list(self.metrics["api_calls"])
        total_api_calls = len(api_calls)
        successful_api_calls = sum(1 for call in api_calls if call["success"])
        api_success_rate = (successful_api_calls / total_api_calls * 100) if total_api_calls > 0 else 100
        
        # Calculate average API response time
        api_response_times = [call["response_time"] for call in api_calls]
        avg_api_response_time = sum(api_response_times) / len(api_response_times) if api_response_times else 0
        
        return {
            "response_time": round(avg_response_time, 2),
            "cpu_usage": round(cpu_usage, 2),
            "memory_usage": round(memory_usage, 2),
            "api_success_rate": round(api_success_rate, 2),
            "api_response_time": round(avg_api_response_time, 2),
            "uptime": self._format_timedelta(datetime.now() - self.start_time),
            "last_update": datetime.now().isoformat(),
        }
    
    def get_metric_history(self, metric_name: str, count: int = 100) -> List[Dict]:
        """
        Get historical data for a specific metric.
        
        Args:
            metric_name: Name of the metric
            count: Number of samples to retrieve
            
        Returns:
            List of metric samples
        """
        if metric_name not in self.metrics:
            return []
        
        # Return most recent samples
        return list(reversed(list(self.metrics[metric_name])))[:count]
    
    def reset_metrics(self):
        """Reset all metrics."""
        for metric in self.metrics:
            self.metrics[metric].clear()
        
        self.start_time = datetime.now()
        self.last_update = datetime.now()
        
        logger.info("Performance metrics reset")
    
    def _format_timedelta(self, td: timedelta) -> str:
        """
        Format a timedelta object as a human-readable string.
        
        Args:
            td: Timedelta object
            
        Returns:
            Formatted string
        """
        total_seconds = int(td.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


def main():
    """Main function for testing the monitor module."""
    # Create system monitor
    monitor = SystemMonitor()
    
    # Log some test activities
    monitor.log_activity(user_id=12345, activity="start_command")
    monitor.log_activity(user_id=67890, activity="help_command")
    monitor.log_activity(user_id=12345, activity="settings_command")
    
    # Log an error
    monitor.log_error("Test error message", user_id=12345)
    
    # Get system status
    status = monitor.get_system_status()
    logger.info(f"System status: {status}")
    
    # Create performance tracker
    tracker = PerformanceTracker()
    
    # Track some test metrics
    start_time = time.time()
    time.sleep(0.1)  # Simulate some work
    tracker.track_response_time(start_time)
    
    # Track an API call
    tracker.track_api_call("test_api", True, 150.5)
    
    # Get performance metrics
    metrics = tracker.get_metrics()
    logger.info(f"Performance metrics: {metrics}")
    
    logger.info("Monitor module test completed successfully")


if __name__ == "__main__":
    main()
