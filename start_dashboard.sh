#!/bin/bash
# start_dashboard.sh - Script to start the monitoring dashboard for the Telegram bot

# Set up environment
echo "Setting up environment for Telegram bot monitoring dashboard..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if required files exist
if [ ! -f "monitor.py" ]; then
    echo "Error: monitor.py not found."
    exit 1
fi

# Create dashboard directory if it doesn't exist
mkdir -p dashboard

# Check if dashboard dependencies are installed
echo "Checking dashboard dependencies..."
pip install flask plotly pandas psutil --quiet

# Set up logging directory
mkdir -p logs

# Create simple Flask dashboard app if it doesn't exist
if [ ! -f "dashboard/app.py" ]; then
    echo "Creating dashboard application..."
    cat > dashboard/app.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Bot Monitoring Dashboard
--------------------------------
A simple Flask-based dashboard for monitoring the Telegram bot.
"""

import os
import sys
import json
import time
import psutil
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import monitoring module
import monitor

# Create Flask app
app = Flask(__name__)

# Create system monitor
system_monitor = monitor.SystemMonitor()

# Create performance tracker
performance_tracker = monitor.PerformanceTracker()

@app.route('/')
def index():
    """Render dashboard homepage."""
    return render_template('index.html')

@app.route('/api/system-status')
def system_status():
    """Get current system status."""
    return jsonify(system_monitor.get_system_status())

@app.route('/api/performance-metrics')
def performance_metrics():
    """Get current performance metrics."""
    return jsonify(performance_tracker.get_metrics())

@app.route('/api/user-statistics')
def user_statistics():
    """Get user statistics."""
    return jsonify(system_monitor.get_user_statistics())

@app.route('/api/usage-statistics')
def usage_statistics():
    """Get usage statistics."""
    return jsonify(system_monitor.get_usage_statistics())

@app.route('/api/recent-logs')
def recent_logs():
    """Get recent logs."""
    count = request.args.get('count', default=10, type=int)
    level = request.args.get('level', default=None, type=str)
    user_id = request.args.get('user_id', default=None, type=int)
    
    return jsonify(system_monitor.get_recent_logs(count=count, level=level, user_id=user_id))

@app.route('/api/toggle-maintenance')
def toggle_maintenance():
    """Toggle maintenance mode."""
    new_state = system_monitor.toggle_maintenance_mode()
    return jsonify({"maintenance_mode": new_state})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create index.html if it doesn't exist
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Bot Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { padding-top: 20px; }
        .card { margin-bottom: 20px; }
        .status-normal { color: green; }
        .status-warning { color: orange; }
        .status-critical { color: red; }
        .status-maintenance { color: blue; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">Telegram Bot Monitoring Dashboard</h1>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        System Status
                    </div>
                    <div class="card-body">
                        <h5 class="card-title">Status: <span id="status-badge" class="badge bg-success">Normal</span></h5>
                        <p class="card-text">
                            <strong>Uptime:</strong> <span id="uptime">Loading...</span><br>
                            <strong>CPU Usage:</strong> <span id="cpu-usage">Loading...</span><br>
                            <strong>Memory Usage:</strong> <span id="memory-usage">Loading...</span><br>
                            <strong>Disk Usage:</strong> <span id="disk-usage">Loading...</span><br>
                            <strong>Active Users:</strong> <span id="active-users">Loading...</span><br>
                            <strong>Errors:</strong> <span id="error-count">Loading...</span><br>
                            <strong>Warnings:</strong> <span id="warning-count">Loading...</span>
                        </p>
                        <button id="toggle-maintenance" class="btn btn-primary">Toggle Maintenance Mode</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        Performance Metrics
                    </div>
                    <div class="card-body">
                        <canvas id="performance-chart"></canvas>
                        <p class="card-text mt-3">
                            <strong>Avg. Response Time:</strong> <span id="response-time">Loading...</span> ms<br>
                            <strong>API Success Rate:</strong> <span id="api-success-rate">Loading...</span>%<br>
                            <strong>API Response Time:</strong> <span id="api-response-time">Loading...</span> ms
                        </p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        Recent Logs
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Timestamp</th>
                                        <th>Level</th>
                                        <th>Message</th>
                                        <th>User ID</th>
                                    </tr>
                                </thead>
                                <tbody id="logs-table-body">
                                    <tr>
                                        <td colspan="4" class="text-center">Loading logs...</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Update data every 5 seconds
        const updateInterval = 5000;
        let performanceChart = null;
        
        // Initialize charts
        function initCharts() {
            const ctx = document.getElementById('performance-chart').getContext('2d');
            performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: Array(10).fill(''),
                    datasets: [{
                        label: 'CPU Usage (%)',
                        data: Array(10).fill(0),
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        tension: 0.4
                    }, {
                        label: 'Memory Usage (%)',
                        data: Array(10).fill(0),
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
        
        // Update system status
        function updateSystemStatus() {
            fetch('/api/system-status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('uptime').textContent = data.uptime;
                    document.getElementById('cpu-usage').textContent = data.cpu_percent + '%';
                    document.getElementById('memory-usage').textContent = data.memory_percent + '%';
                    document.getElementById('disk-usage').textContent = data.disk_percent + '%';
                    document.getElementById('active-users').textContent = data.active_users;
                    document.getElementById('error-count').textContent = data.error_count;
                    document.getElementById('warning-count').textContent = data.warning_count;
                    
                    // Update status badge
                    const statusBadge = document.getElementById('status-badge');
                    statusBadge.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
                    
                    if (data.status === 'normal') {
                        statusBadge.className = 'badge bg-success';
                    } else if (data.status === 'warning') {
                        statusBadge.className = 'badge bg-warning';
                    } else if (data.status === 'critical') {
                        statusBadge.className = 'badge bg-danger';
                    } else if (data.status === 'maintenance') {
                        statusBadge.className = 'badge bg-info';
                    }
                    
                    // Update maintenance button
                    const maintenanceButton = document.getElementById('toggle-maintenance');
                    if (data.maintenance_mode) {
                        maintenanceButton.textContent = 'Disable Maintenance Mode';
                        maintenanceButton.className = 'btn btn-warning';
                    } else {
                        maintenanceButton.textContent = 'Enable Maintenance Mode';
                        maintenanceButton.className = 'btn btn-primary';
                    }
                })
                .catch(error => console.error('Error fetching system status:', error));
        }
        
        // Update performance metrics
        function updatePerformanceMetrics() {
            fetch('/api/performance-metrics')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('response-time').textContent = data.response_time;
                    document.getElementById('api-success-rate').textContent = data.api_success_rate;
                    document.getElementById('api-response-time').textContent = data.api_response_time;
                    
                    // Update chart
                    if (performanceChart) {
                        // Add new data points
                        performanceChart.data.datasets[0].data.push(data.cpu_usage);
                        performanceChart.data.datasets[1].data.push(data.memory_usage);
                        
                        // Remove old data points
                        if (performanceChart.data.datasets[0].data.length > 10) {
                            performanceChart.data.datasets[0].data.shift();
                            performanceChart.data.datasets[1].data.shift();
                        }
                        
                        // Update labels
                        const now = new Date();
                        const timeString = now.getHours().toString().padStart(2, '0') + ':' + 
                                          now.getMinutes().toString().padStart(2, '0') + ':' + 
                                          now.getSeconds().toString().padStart(2, '0');
                        
                        performanceChart.data.labels.push(timeString);
                        if (performanceChart.data.labels.length > 10) {
                            performanceChart.data.labels.shift();
                        }
                        
                        performanceChart.update();
                    }
                })
                .catch(error => console.error('Error fetching performance metrics:', error));
        }
        
        // Update recent logs
        function updateRecentLogs() {
            fetch('/api/recent-logs?count=10')
                .then(response => response.json())
                .then(logs => {
                    const tableBody = document.getElementById('logs-table-body');
                    tableBody.innerHTML = '';
                    
                    logs.forEach(log => {
                        const row = document.createElement('tr');
                        
                        // Format timestamp
                        const timestamp = new Date(log.timestamp);
                        const formattedTime = timestamp.toLocaleString();
                        
                        // Create cells
                        const timestampCell = document.createElement('td');
                        timestampCell.textContent = formattedTime;
                        
                        const levelCell = document.createElement('td');
                        levelCell.textContent = log.level;
                        
                        // Set level cell color
                        if (log.level === 'ERROR') {
                            levelCell.className = 'text-danger';
                        } else if (log.level === 'WARNING') {
                            levelCell.className = 'text-warning';
                        } else if (log.level === 'INFO') {
                            levelCell.className = 'text-info';
                        }
                        
                        const messageCell = document.createElement('td');
                        messageCell.textContent = log.message;
                        
                        const userIdCell = document.createElement('td');
                        userIdCell.textContent = log.user_id || '-';
                        
                        // Add cells to row
                        row.appendChild(timestampCell);
                        row.appendChild(levelCell);
                        row.appendChild(messageCell);
                        row.appendChild(userIdCell);
                        
                        // Add row to table
                        tableBody.appendChild(row);
                    });
                    
                    if (logs.length === 0) {
                        const row = document.createElement('tr');
                        const cell = document.createElement('td');
                        cell.colSpan = 4;
                        cell.className = 'text-center';
                        cell.textContent = 'No logs available';
                        row.appendChild(cell);
                        tableBody.appendChild(row);
                    }
                })
                .catch(error => console.error('Error fetching logs:', error));
        }
        
        // Toggle maintenance mode
        document.getElementById('toggle-maintenance').addEventListener('click', function() {
            fetch('/api/toggle-maintenance')
                .then(response => response.json())
                .then(data => {
                    updateSystemStatus();
                })
                .catch(error => console.error('Error toggling maintenance mode:', error));
        });
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            updateSystemStatus();
            updatePerformanceMetrics();
            updateRecentLogs();
            
            // Set up periodic updates
            setInterval(updateSystemStatus, updateInterval);
            setInterval(updatePerformanceMetrics, updateInterval);
            setInterval(updateRecentLogs, updateInterval);
        });
    </script>
</body>
</html>""")
    
    # Start the dashboard
    print("Starting monitoring dashboard on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF
    echo "Dashboard application created."
fi

# Make dashboard app executable
chmod +x dashboard/app.py

# Start the dashboard
echo "Starting Telegram bot monitoring dashboard..."
cd dashboard && python3 app.py

# Exit with the same status as the dashboard
exit $?
