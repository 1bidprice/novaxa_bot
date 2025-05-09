// Main JavaScript file for the Telegram Bot Dashboard

document.addEventListener('DOMContentLoaded', function() {
  // Initialize charts
  initializeCharts();
  
  // Set up event listeners
  setupEventListeners();
  
  // Initialize real-time updates
  initializeRealTimeUpdates();
});

// Chart initialization
function initializeCharts() {
  // User activity chart
  const userActivityCtx = document.getElementById('userActivityChart');
  if (userActivityCtx) {
    new Chart(userActivityCtx, {
      type: 'line',
      data: {
        labels: ['Δευτέρα', 'Τρίτη', 'Τετάρτη', 'Πέμπτη', 'Παρασκευή', 'Σάββατο', 'Κυριακή'],
        datasets: [{
          label: 'Ενεργοί Χρήστες',
          data: [65, 59, 80, 81, 56, 55, 40],
          fill: false,
          borderColor: '#0088cc',
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
  
  // Command usage chart
  const commandUsageCtx = document.getElementById('commandUsageChart');
  if (commandUsageCtx) {
    new Chart(commandUsageCtx, {
      type: 'doughnut',
      data: {
        labels: ['/start', '/help', '/settings', '/info', 'Άλλες εντολές'],
        datasets: [{
          data: [30, 20, 15, 25, 10],
          backgroundColor: [
            '#0088cc',
            '#1e96c8',
            '#4caf50',
            '#ff9800',
            '#f44336'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right'
          }
        }
      }
    });
  }
  
  // Response time chart
  const responseTimeCtx = document.getElementById('responseTimeChart');
  if (responseTimeCtx) {
    new Chart(responseTimeCtx, {
      type: 'bar',
      data: {
        labels: ['< 1s', '1-2s', '2-3s', '3-5s', '> 5s'],
        datasets: [{
          label: 'Χρόνος Απόκρισης',
          data: [45, 30, 15, 8, 2],
          backgroundColor: '#0088cc'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
}

// Event listeners setup
function setupEventListeners() {
  // Navigation
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', function() {
      navItems.forEach(i => i.classList.remove('active'));
      this.classList.add('active');
      
      // Show corresponding section
      const targetSection = this.getAttribute('data-target');
      document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
      });
      document.getElementById(targetSection).style.display = 'block';
    });
  });
  
  // Chart filters
  const chartFilters = document.querySelectorAll('.chart-filter');
  chartFilters.forEach(filter => {
    filter.addEventListener('click', function() {
      const filterGroup = this.closest('.chart-filters').querySelectorAll('.chart-filter');
      filterGroup.forEach(f => f.classList.remove('active'));
      this.classList.add('active');
      
      // Update chart data based on filter
      const chartId = this.closest('.chart-container').querySelector('.chart').id;
      updateChartData(chartId, this.getAttribute('data-period'));
    });
  });
  
  // Dark mode toggle
  const darkModeToggle = document.getElementById('darkModeToggle');
  if (darkModeToggle) {
    darkModeToggle.addEventListener('change', function() {
      document.body.classList.toggle('dark-mode', this.checked);
      localStorage.setItem('darkMode', this.checked ? 'enabled' : 'disabled');
    });
    
    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
      darkModeToggle.checked = true;
      document.body.classList.add('dark-mode');
    }
  }
  
  // Form submissions
  const configForm = document.getElementById('configForm');
  if (configForm) {
    configForm.addEventListener('submit', function(e) {
      e.preventDefault();
      saveConfiguration(this);
    });
  }
  
  const messageForm = document.getElementById('messageForm');
  if (messageForm) {
    messageForm.addEventListener('submit', function(e) {
      e.preventDefault();
      sendBroadcastMessage(this);
    });
  }
}

// Real-time updates
function initializeRealTimeUpdates() {
  // Simulate real-time updates for demo purposes
  setInterval(updateStatistics, 5000);
}

// Update chart data based on selected time period
function updateChartData(chartId, period) {
  // In a real application, this would fetch data from the server
  console.log(`Updating chart ${chartId} with period ${period}`);
  
  // Simulate data update
  const chart = Chart.getChart(chartId);
  if (chart) {
    if (chart.config.type === 'line') {
      // Generate random data for demonstration
      const newData = Array(7).fill(0).map(() => Math.floor(Math.random() * 100));
      chart.data.datasets[0].data = newData;
      chart.update();
    }
  }
}

// Save bot configuration
function saveConfiguration(form) {
  const formData = new FormData(form);
  const config = Object.fromEntries(formData.entries());
  
  // In a real application, this would send data to the server
  console.log('Saving configuration:', config);
  
  // Show success message
  showNotification('Οι ρυθμίσεις αποθηκεύτηκαν επιτυχώς!', 'success');
}

// Send broadcast message
function sendBroadcastMessage(form) {
  const formData = new FormData(form);
  const message = formData.get('message');
  const targetUsers = formData.get('targetUsers');
  
  // In a real application, this would send data to the server
  console.log(`Sending message "${message}" to ${targetUsers}`);
  
  // Show success message
  showNotification('Το μήνυμα στάλθηκε επιτυχώς!', 'success');
  
  // Reset form
  form.reset();
}

// Update statistics (simulated real-time updates)
function updateStatistics() {
  // Update active users
  const activeUsersElement = document.getElementById('activeUsers');
  if (activeUsersElement) {
    const currentValue = parseInt(activeUsersElement.textContent);
    const change = Math.floor(Math.random() * 10) - 5; // Random change between -5 and +5
    activeUsersElement.textContent = Math.max(0, currentValue + change);
  }
  
  // Update message count
  const messageCountElement = document.getElementById('messageCount');
  if (messageCountElement) {
    const currentValue = parseInt(messageCountElement.textContent);
    const increase = Math.floor(Math.random() * 5); // Random increase between 0 and 4
    messageCountElement.textContent = currentValue + increase;
  }
  
  // Update bot status indicator randomly (for demo purposes)
  const statusIndicator = document.getElementById('botStatus');
  if (statusIndicator && Math.random() < 0.05) { // 5% chance to change status
    const statuses = ['status-online', 'status-warning', 'status-error'];
    const statusTexts = ['Σε λειτουργία', 'Προειδοποίηση', 'Σφάλμα'];
    
    // Remove all status classes
    statuses.forEach(status => {
      statusIndicator.classList.remove(status);
    });
    
    // Randomly select a new status
    const randomIndex = Math.floor(Math.random() * 3);
    statusIndicator.classList.add(statuses[randomIndex]);
    statusIndicator.textContent = statusTexts[randomIndex];
  }
}

// Show notification
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  // Animate in
  setTimeout(() => {
    notification.classList.add('show');
  }, 10);
  
  // Remove after 3 seconds
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 3000);
}
