/* NOVAXA Dashboard JavaScript */

// DOM Elements
const navLinks = document.querySelectorAll('.nav-links li');
const pages = document.querySelectorAll('.page');
const viewAllLinks = document.querySelectorAll('.view-all');
const currentDateElement = document.getElementById('current-date');
const darkModeToggle = document.getElementById('dark-mode-toggle');
const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
const refreshIntervalSelect = document.getElementById('refresh-interval');
const addStockButton = document.getElementById('add-stock');
const addStockModal = document.getElementById('add-stock-modal');
const addStockForm = document.getElementById('add-stock-form');
const refreshStocksButton = document.getElementById('refresh-stocks');
const refreshAlertsButton = document.getElementById('refresh-alerts');
const sendBroadcastButton = document.getElementById('send-broadcast');
const sendBroadcastModal = document.getElementById('send-broadcast-modal');
const broadcastForm = document.getElementById('broadcast-form');
const updateTokenBtn = document.getElementById('update-token-btn');
const updateTokenModal = document.getElementById('update-token-modal');
const updateTokenForm = document.getElementById('update-token-form');
const saveSettingsButton = document.getElementById('save-settings');
const resetSettingsButton = document.getElementById('reset-settings');
const closeModalButtons = document.querySelectorAll('.close-modal, .cancel-button');

// API Endpoints
const API_ENDPOINTS = {
    stocks: '/api/proxy/stocks',
    stock: (symbol) => `/api/proxy/stocks/${symbol}`,
    projects: '/api/proxy/projects',
    project: (id) => `/api/proxy/projects/${id}`,
    alerts: '/api/proxy/alerts',
    addStock: '/api/proxy/add_stock',
    setAlert: '/api/proxy/set_alert',
    updateProject: '/api/proxy/update_project',
    sendTelegramMessage: '/api/send_telegram_message',
    getTelegramUpdates: '/api/get_telegram_updates'
};

// App State
let appState = {
    currentPage: 'dashboard',
    stocks: {},
    projects: {},
    alerts: [],
    settings: {
        darkMode: false,
        autoRefresh: true,
        refreshInterval: 5,
        stockAlerts: true,
        projectAlerts: true,
        systemAlerts: true
    },
    refreshTimers: {}
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    // Set current date
    setCurrentDate();
    
    // Load settings from localStorage
    loadSettings();
    
    // Initialize page navigation
    initNavigation();
    
    // Initialize modals
    initModals();
    
    // Initialize forms
    initForms();
    
    // Load initial data
    loadDashboardData();
    
    // Set up auto-refresh
    setupAutoRefresh();
});

// Set current date
function setCurrentDate() {
    if (currentDateElement) {
        const now = new Date();
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        currentDateElement.textContent = now.toLocaleDateString('el-GR', options);
    }
}

// Load settings from localStorage
function loadSettings() {
    const savedSettings = localStorage.getItem('novaxaSettings');
    if (savedSettings) {
        appState.settings = { ...appState.settings, ...JSON.parse(savedSettings) };
    }
    
    // Apply settings
    if (darkModeToggle) {
        darkModeToggle.checked = appState.settings.darkMode;
        if (appState.settings.darkMode) {
            document.body.classList.add('dark-mode');
        }
    }
    
    if (autoRefreshToggle) {
        autoRefreshToggle.checked = appState.settings.autoRefresh;
    }
    
    if (refreshIntervalSelect) {
        refreshIntervalSelect.value = appState.settings.refreshInterval;
    }
    
    // Apply other settings
    const stockAlertsToggle = document.getElementById('stock-alerts-toggle');
    if (stockAlertsToggle) {
        stockAlertsToggle.checked = appState.settings.stockAlerts;
    }
    
    const projectAlertsToggle = document.getElementById('project-alerts-toggle');
    if (projectAlertsToggle) {
        projectAlertsToggle.checked = appState.settings.projectAlerts;
    }
    
    const systemAlertsToggle = document.getElementById('system-alerts-toggle');
    if (systemAlertsToggle) {
        systemAlertsToggle.checked = appState.settings.systemAlerts;
    }
}

// Save settings to localStorage
function saveSettings() {
    localStorage.setItem('novaxaSettings', JSON.stringify(appState.settings));
}

// Initialize page navigation
function initNavigation() {
    // Nav links click handler
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const targetPage = link.getAttribute('data-page');
            changePage(targetPage);
        });
    });
    
    // View all links click handler
    viewAllLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetPage = link.getAttribute('data-target');
            changePage(targetPage);
        });
    });
}

// Change active page
function changePage(pageName) {
    // Update active nav link
    navLinks.forEach(link => {
        if (link.getAttribute('data-page') === pageName) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Update active page
    pages.forEach(page => {
        if (page.id === `${pageName}-page`) {
            page.classList.add('active');
        } else {
            page.classList.remove('active');
        }
    });
    
    // Update app state
    appState.currentPage = pageName;
    
    // Load page-specific data
    switch (pageName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'stocks':
            loadStocksData();
            break;
        case 'projects':
            loadProjectsData();
            break;
        case 'alerts':
            loadAlertsData();
            break;
        case 'settings':
            // Settings page doesn't need to load data
            break;
    }
}

// Initialize modals
function initModals() {
    // Close modal buttons
    closeModalButtons.forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            if (modal) {
                modal.classList.remove('active');
            }
        });
    });
    
    // Add stock button
    if (addStockButton) {
        addStockButton.addEventListener('click', () => {
            if (addStockModal) {
                addStockModal.classList.add('active');
            }
        });
    }
    
    // Send broadcast button
    if (sendBroadcastButton) {
        sendBroadcastButton.addEventListener('click', () => {
            if (sendBroadcastModal) {
                sendBroadcastModal.classList.add('active');
            }
        });
    }
    
    // Update token button
    if (updateTokenBtn) {
        updateTokenBtn.addEventListener('click', () => {
            if (updateTokenModal) {
                updateTokenModal.classList.add('active');
            }
        });
    }
    
    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        document.querySelectorAll('.modal.active').forEach(modal => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
}

// Initialize forms
function initForms() {
    // Add stock form
    if (addStockForm) {
        addStockForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const symbol = document.getElementById('stock-symbol').value.toUpperCase();
            const name = document.getElementById('stock-name').value;
            const threshold = parseFloat(document.getElementById('stock-threshold').value) || null;
            
            addStock(symbol, name, threshold);
        });
    }
    
    // Broadcast form
    if (broadcastForm) {
        broadcastForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const message = document.getElementById('broadcast-message').value;
            
            sendBroadcast(message);
        });
    }
    
    // Update token form
    if (updateTokenForm) {
        updateTokenForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const newToken = document.getElementById('new-token').value;
            
            updateBotToken(newToken);
        });
    }
    
    // Settings form
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', () => {
            appState.settings.darkMode = darkModeToggle.checked;
            if (darkModeToggle.checked) {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
            saveSettings();
        });
    }
    
    if (autoRefreshToggle) {
        autoRefreshToggle.addEventListener('change', () => {
            appState.settings.autoRefresh = autoRefreshToggle.checked;
            saveSettings();
            setupAutoRefresh();
        });
    }
    
    if (refreshIntervalSelect) {
        refreshIntervalSelect.addEventListener('change', () => {
            appState.settings.refreshInterval = parseInt(refreshIntervalSelect.value);
            saveSettings();
            setupAutoRefresh();
        });
    }
    
    // Stock alerts toggle
    const stockAlertsToggle = document.getElementById('stock-alerts-toggle');
    if (stockAlertsToggle) {
        stockAlertsToggle.addEventListener('change', () => {
            appState.settings.stockAlerts = stockAlertsToggle.checked;
            saveSettings();
        });
    }
    
    // Project alerts toggle
    const projectAlertsToggle = document.getElementById('project-alerts-toggle');
    if (projectAlertsToggle) {
        projectAlertsToggle.addEventListener('change', () => {
            appState.settings.projectAlerts = projectAlertsToggle.checked;
            saveSettings();
        });
    }
    
    // System alerts toggle
    const systemAlertsToggle = document.getElementById('system-alerts-toggle');
    if (systemAlertsToggle) {
        systemAlertsToggle.addEventListener('change', () => {
            appState.settings.systemAlerts = systemAlertsToggle.checked;
            saveSettings();
        });
    }
    
    // Save settings button
    if (saveSettingsButton) {
        saveSettingsButton.addEventListener('click', () => {
            saveSettings();
            showNotification('Οι ρυθμίσεις αποθηκεύτηκαν επιτυχώς!', 'success');
        });
    }
    
    // Reset settings button
    if (resetSettingsButton) {
        resetSettingsButton.addEventListener('click', () => {
            // Reset to default settings
            appState.settings = {
                darkMode: false,
                autoRefresh: true,
                refreshInterval: 5,
                stockAlerts: true,
                projectAlerts: true,
                systemAlerts: true
            };
            
            // Apply reset settings
            if (darkModeToggle) {
                darkModeToggle.checked = false;
                document.body.classList.remove('dark-mode');
            }
            
            if (autoRefreshToggle) {
                autoRefreshToggle.checked = true;
            }
            
            if (refreshIntervalSelect) {
                refreshIntervalSelect.value = 5;
            }
            
            if (stockAlertsToggle) {
                stockAlertsToggle.checked = true;
            }
            
            if (projectAlertsToggle) {
                projectAlertsToggle.checked = true;
            }
            
            if (systemAlertsToggle) {
                systemAlertsToggle.checked = true;
            }
            
            saveSettings();
            setupAutoRefresh();
            showNotification('Οι ρυθμίσεις επαναφέρθηκαν στις προεπιλογές!', 'success');
        });
    }
    
    // Refresh buttons
    if (refreshStocksButton) {
        refreshStocksButton.addEventListener('click', () => {
            loadStocksData();
        });
    }
    
    if (refreshAlertsButton) {
        refreshAlertsButton.addEventListener('click', () => {
            loadAlertsData();
        });
    }
}

// Setup auto-refresh
function setupAutoRefresh() {
    // Clear existing timers
    Object.values(appState.refreshTimers).forEach(timer => {
        clearInterval(timer);
    });
    
    // If auto-refresh is disabled, return
    if (!appState.settings.autoRefresh) {
        return;
    }
    
    // Set refresh interval in milliseconds
    const interval = appState.settings.refreshInterval * 60 * 1000;
    
    // Set up timers for different data types
    appState.refreshTimers.dashboard = setInterval(() => {
        if (appState.currentPage === 'dashboard') {
            loadDashboardData();
        }
    }, interval);
    
    appState.refreshTimers.stocks = setInterval(() => {
        if (appState.currentPage === 'stocks') {
            loadStocksData();
        }
    }, interval);
    
    appState.refreshTimers.projects = setInterval(() => {
        if (appState.currentPage === 'projects') {
            loadProjectsData();
        }
    }, interval);
    
    appState.refreshTimers.alerts = setInterval(() => {
        if (appState.currentPage === 'alerts') {
            loadAlertsData();
        }
    }, interval);
    
    // Update ticker every minute regardless of page
    appState.refreshTimers.ticker = setInterval(() => {
        updateStockTicker();
    }, 60 * 1000);
}

// Load dashboard data
function loadDashboardData() {
    // Load stocks overview
    fetchData(API_ENDPOINTS.stocks, (data) => {
        if (data.status === 'success') {
            appState.stocks = data.data;
            updateStockTicker();
            updateStocksOverview();
        }
    });
    
    // Load projects overview
    fetchData(API_ENDPOINTS.projects, (data) => {
        if (data.status === 'success') {
            appState.projects = data.data;
            updateProjectsOverview();
        }
    });
    
    // Load alerts
    fetchData(API_ENDPOINTS.alerts, (data) => {
        if (data.status === 'success') {
            appState.alerts = data.data;
            updateAlertsOverview();
        }
    });
    
    // Update progress overview
    updateProgressOverview();
}

// Load stocks data
function loadStocksData() {
    fetchData(API_ENDPOINTS.stocks, (data) => {
        if (data.status === 'success') {
            appState.stocks = data.data;
            updateStockTicker();
            renderStocksPage();
        }
    });
}

// Load projects data
function loadProjectsData() {
    fetchData(API_ENDPOINTS.projects, (data) => {
        if (data.status === 'success') {
            appState.projects = data.data;
            renderProjectsPage();
        }
    });
}

// Load alerts data
function loadAlertsData() {
    fetchData(API_ENDPOINTS.alerts, (data) => {
        if (data.status === 'success') {
            appState.alerts = data.data;
            renderAlertsPage();
        }
    });
}

// Update stock ticker
function updateStockTicker() {
    const opapTicker = document.getElementById('ticker-opap');
    const metlenTicker = document.getElementById('ticker-metlen');
    
    if (opapTicker && appState.stocks['OPAP.AT']) {
        const stock = appState.stocks['OPAP.AT'];
        const priceElement = opapTicker.querySelector('.ticker-price');
        const changeElement = opapTicker.querySelector('.ticker-change');
        
        if (priceElement) {
            priceElement.textContent = `${stock.price.toFixed(2)}€`;
        }
        
        if (changeElement) {
            const changeText = `${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}€ (${stock.change_percent.toFixed(2)}%)`;
            changeElement.textContent = changeText;
            
            if (stock.change > 0) {
                changeElement.classList.add('positive');
                changeElement.classList.remove('negative');
            } else if (stock.change < 0) {
                changeElement.classList.add('negative');
                changeElement.classList.remove('positive');
            } else {
                changeElement.classList.remove('positive');
                changeElement.classList.remove('negative');
            }
        }
    }
    
    if (metlenTicker && appState.stocks['MYTIL.AT']) {
        const stock = appState.stocks['MYTIL.AT'];
        const priceElement = metlenTicker.querySelector('.ticker-price');
        const changeElement = metlenTicker.querySelector('.ticker-change');
        
        if (priceElement) {
            priceElement.textContent = `${stock.price.toFixed(2)}€`;
        }
        
        if (changeElement) {
            const changeText = `${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}€ (${stock.change_percent.toFixed(2)}%)`;
            changeElement.textContent = changeText;
            
            if (stock.change > 0) {
                changeElement.classList.add('positive');
                changeElement.classList.remove('negative');
            } else if (stock.change < 0) {
                changeElement.classList.add('negative');
                changeElement.classList.remove('positive');
            } else {
                changeElement.classList.remove('positive');
                changeElement.classList.remove('negative');
            }
        }
    }
}

// Update stocks overview on dashboard
function updateStocksOverview() {
    const container = document.getElementById('stocks-overview-content');
    if (!container) return;
    
    if (Object.keys(appState.stocks).length === 0) {
        container.innerHTML = '<div class="no-data">Δεν υπάρχουν διαθέσιμα δεδομένα μετοχών.</div>';
        return;
    }
    
    let html = '';
    
    // Show only 2 stocks in overview
    const stockSymbols = Object.keys(appState.stocks).slice(0, 2);
    
    stockSymbols.forEach(symbol => {
        const stock = appState.stocks[symbol];
        const changeClass = stock.change > 0 ? 'positive' : stock.change < 0 ? 'negative' : '';
        const changeIcon = stock.change > 0 ? 'fa-arrow-up' : stock.change < 0 ? 'fa-arrow-down' : 'fa-minus';
        
        html += `
            <div class="stock-item">
                <div class="stock-header">
                    <div class="stock-name">${stock.name}</div>
                    <div class="stock-symbol">${symbol}</div>
                </div>
                <div class="stock-price">${stock.price.toFixed(2)}€</div>
                <div class="stock-change ${changeClass}">
                    <i class="fas ${changeIcon}"></i>
                    ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}€ (${stock.change_percent.toFixed(2)}%)
                </div>
                <div class="stock-updated">
                    Τελευταία ενημέρωση: ${stock.timestamp}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Update projects overview on dashboard
function updateProjectsOverview() {
    const container = document.getElementById('projects-overview-content');
    if (!container) return;
    
    if (Object.keys(appState.projects).length === 0) {
        container.innerHTML = '<div class="no-data">Δεν υπάρχουν διαθέσιμα δεδομένα projects.</div>';
        return;
    }
    
    let html = '';
    
    // Show all projects in overview
    Object.keys(appState.projects).forEach(projectId => {
        const project = appState.projects[projectId];
        const statusClass = project.status === 'Active' ? 'active' : project.status === 'In Development' ? 'development' : 'planning';
        
        html += `
            <div class="project-item">
                <div class="project-header">
                    <div class="project-name">
                        <span class="status-indicator ${statusClass}"></span>
                        ${project.name}
                    </div>
                    <div class="project-status">${project.status}</div>
                </div>
                <div class="project-progress">
                    <div class="progress-label">
                        <span>Πρόοδος</span>
                        <span>${project.metrics.progress}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-value" style="width: ${project.metrics.progress}%"></div>
                    </div>
                </div>
                <div class="project-updated">
                    Τελευταία ενημέρωση: ${project.last_update}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Update alerts overview on dashboard
function updateAlertsOverview() {
    const container = document.getElementById('alerts-overview-content');
    if (!container) return;
    
    if (appState.alerts.length === 0) {
        container.innerHTML = '<div class="no-data">Δεν υπάρχουν διαθέσιμες ειδοποιήσεις.</div>';
        return;
    }
    
    let html = '';
    
    // Show up to 3 alerts in overview
    const recentAlerts = appState.alerts.slice(0, 3);
    
    recentAlerts.forEach(alert => {
        html += `
            <div class="alert-item">
                <div class="alert-message">${alert}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Update notification count
    const notificationCount = document.querySelector('.notification-count');
    if (notificationCount) {
        notificationCount.textContent = appState.alerts.length;
    }
}

// Update progress overview on dashboard
function updateProgressOverview() {
    const container = document.getElementById('progress-overview-content');
    if (!container) return;
    
    if (Object.keys(appState.projects).length === 0) {
        container.innerHTML = '<div class="no-data">Δεν υπάρχουν διαθέσιμα δεδομένα προόδου.</div>';
        return;
    }
    
    let html = '<div class="progress-summary">';
    
    // Calculate overall progress
    let totalProgress = 0;
    Object.keys(appState.projects).forEach(projectId => {
        totalProgress += appState.projects[projectId].metrics.progress;
    });
    
    const averageProgress = totalProgress / Object.keys(appState.projects).length;
    
    html += `
        <div class="overall-progress">
            <div class="progress-label">
                <span>Συνολική Πρόοδος</span>
                <span>${averageProgress.toFixed(0)}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-value" style="width: ${averageProgress}%"></div>
            </div>
        </div>
    `;
    
    // Add project-specific progress
    html += '<div class="project-progress-list">';
    
    Object.keys(appState.projects).forEach(projectId => {
        const project = appState.projects[projectId];
        
        html += `
            <div class="project-progress-item">
                <div class="progress-label">
                    <span>${project.name}</span>
                    <span>${project.metrics.progress}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-value" style="width: ${project.metrics.progress}%"></div>
                </div>
            </div>
        `;
    });
    
    html += '</div></div>';
    
    container.innerHTML = html;
}

// Render stocks page
function renderStocksPage() {
    const container = document.getElementById('stocks-container');
    if (!container) return;
    
    if (Object.keys(appState.stocks).length === 0) {
        container.innerHTML = '<div class="no-data">Δεν υπάρχουν διαθέσιμα δεδομένα μετοχών.</div>';
        return;
    }
    
    let html = '';
    
    Object.keys(appState.stocks).forEach(symbol => {
        const stock = appState.stocks[symbol];
        const changeClass = stock.change > 0 ? 'positive' : stock.change < 0 ? 'negative' : '';
        const changeIcon = stock.change > 0 ? 'fa-arrow-up' : stock.change < 0 ? 'fa-arrow-down' : 'fa-minus';
        
        html += `
            <div class="stock-card" data-symbol="${symbol}">
                <div class="stock-header">
                    <div>
                        <div class="stock-name">${stock.name}</div>
                        <div class="stock-symbol">${symbol}</div>
                    </div>
                    <div class="stock-actions">
                        <button class="stock-action refresh-stock" data-symbol="${symbol}">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                        <button class="stock-action remove-stock" data-symbol="${symbol}">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="stock-details">
                    <div class="stock-price">${stock.price.toFixed(2)}€</div>
                    <div class="stock-change ${changeClass}">
                        <i class="fas ${changeIcon}"></i>
                        ${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}€ (${stock.change_percent.toFixed(2)}%)
                    </div>
                </div>
                <div class="stock-info">
                    <div>Προηγούμενο κλείσιμο: ${stock.previous_close.toFixed(2)}€</div>
                    <div>Τελευταία ενημέρωση: ${stock.timestamp}</div>
                </div>
                <div class="stock-alert">
                    <div class="alert-title">Όριο Ειδοποίησης</div>
                    <div class="alert-value">
                        <span>${stock.threshold ? stock.threshold.toFixed(2) + '€' : 'Δεν έχει οριστεί'}</span>
                        <button class="alert-edit" data-symbol="${symbol}">Επεξεργασία</button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Add event listeners for stock actions
    document.querySelectorAll('.refresh-stock').forEach(button => {
        button.addEventListener('click', () => {
            const symbol = button.getAttribute('data-symbol');
            refreshStock(symbol);
        });
    });
    
    document.querySelectorAll('.remove-stock').forEach(button => {
        button.addEventListener('click', () => {
            const symbol = button.getAttribute('data-symbol');
            removeStock(symbol);
        });
    });
    
    document.querySelectorAll('.alert-edit').forEach(button => {
        button.addEventListener('click', () => {
            const symbol = button.getAttribute('data-symbol');
            editStockAlert(symbol);
        });
    });
}

// Render projects page
function renderProjectsPage() {
    const container = document.getElementById('projects-container');
    if (!container) return;
    
    if (Object.keys(appState.projects).length === 0) {
        container.innerHTML = '<div class="no-data">Δεν υπάρχουν διαθέσιμα δεδομένα projects.</div>';
        return;
    }
    
    let html = '';
    
    Object.keys(appState.projects).forEach(projectId => {
        const project = appState.projects[projectId];
        const statusClass = project.status === 'Active' ? 'active' : project.status === 'In Development' ? 'development' : 'planning';
        
        html += `
            <div class="project-card" data-project="${projectId}">
                <div class="project-header">
                    <div class="project-name">
                        <span class="status-indicator ${statusClass}"></span>
                        ${project.name}
                    </div>
                    <div class="project-status">${project.status}</div>
                </div>
                <div class="project-description">${project.description}</div>
                <div class="project-progress">
                    <div class="progress-label">
                        <span>Πρόοδος</span>
                        <span>${project.metrics.progress}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-value" style="width: ${project.metrics.progress}%"></div>
                    </div>
                </div>
                <div class="project-metrics">
        `;
        
        // Add project-specific metrics
        if (projectId === 'bidprice') {
            html += `
                <div class="metric">
                    <div class="metric-value">${project.metrics.active_listings}</div>
                    <div class="metric-label">Ενεργές αγγελίες</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${project.metrics.new_bids}</div>
                    <div class="metric-label">Νέες προσφορές</div>
                </div>
            `;
        } else if (projectId === 'amesis') {
            html += `
                <div class="metric">
                    <div class="metric-value">${project.metrics.messages_sent}</div>
                    <div class="metric-label">Μηνύματα</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${project.metrics.recipients}</div>
                    <div class="metric-label">Παραλήπτες</div>
                </div>
            `;
        } else if (projectId === '6225') {
            html += `
                <div class="metric">
                    <div class="metric-value">${project.metrics.products}</div>
                    <div class="metric-label">Προϊόντα</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${project.metrics.sales}</div>
                    <div class="metric-label">Πωλήσεις</div>
                </div>
            `;
        }
        
        html += `
                </div>
                <div class="project-actions">
                    <button class="project-action view-logs" data-project="${projectId}">
                        <i class="fas fa-list"></i> Προβολή Logs
                    </button>
                    <button class="project-action view-details" data-project="${projectId}">
                        <i class="fas fa-info-circle"></i> Λεπτομέρειες
                    </button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Add event listeners for project actions
    document.querySelectorAll('.view-logs').forEach(button => {
        button.addEventListener('click', () => {
            const projectId = button.getAttribute('data-project');
            viewProjectLogs(projectId);
        });
    });
    
    document.querySelectorAll('.view-details').forEach(button => {
        button.addEventListener('click', () => {
            const projectId = button.getAttribute('data-project');
            viewProjectDetails(projectId);
        });
    });
}

// Render alerts page
function renderAlertsPage() {
    const container = document.getElementById('alerts-container');
    if (!container) return;
    
    if (appState.alerts.length === 0) {
        container.innerHTML = '<div class="no-data">Δεν υπάρχουν διαθέσιμες ειδοποιήσεις.</div>';
        return;
    }
    
    let html = '';
    
    appState.alerts.forEach((alert, index) => {
        html += `
            <div class="alert-item" data-index="${index}">
                <div class="alert-header">
                    <div class="alert-type">
                        <i class="fas fa-bell"></i>
                        Ειδοποίηση Μετοχής
                    </div>
                    <div class="alert-time">${new Date().toLocaleString('el-GR')}</div>
                </div>
                <div class="alert-message">${alert}</div>
                <div class="alert-actions">
                    <button class="alert-action dismiss-alert" data-index="${index}">
                        <i class="fas fa-check"></i> Αποδοχή
                    </button>
                    <button class="alert-action delete-alert" data-index="${index}">
                        <i class="fas fa-trash"></i> Διαγραφή
                    </button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Add event listeners for alert actions
    document.querySelectorAll('.dismiss-alert').forEach(button => {
        button.addEventListener('click', () => {
            const index = parseInt(button.getAttribute('data-index'));
            dismissAlert(index);
        });
    });
    
    document.querySelectorAll('.delete-alert').forEach(button => {
        button.addEventListener('click', () => {
            const index = parseInt(button.getAttribute('data-index'));
            deleteAlert(index);
        });
    });
}

// Add stock
function addStock(symbol, name, threshold) {
    const data = {
        symbol: symbol,
        name: name,
        threshold: threshold
    };
    
    fetchData(API_ENDPOINTS.addStock, (response) => {
        if (response.status === 'success') {
            // Close modal
            if (addStockModal) {
                addStockModal.classList.remove('active');
            }
            
            // Reset form
            if (addStockForm) {
                addStockForm.reset();
            }
            
            // Refresh stocks data
            loadStocksData();
            
            // Show notification
            showNotification(`Η μετοχή ${name} (${symbol}) προστέθηκε επιτυχώς!`, 'success');
        } else {
            showNotification(`Σφάλμα: ${response.message}`, 'error');
        }
    }, 'POST', data);
}

// Remove stock
function removeStock(symbol) {
    // In a real implementation, you would call an API endpoint to remove the stock
    // For now, just remove it from the local state
    if (appState.stocks[symbol]) {
        const stockName = appState.stocks[symbol].name;
        delete appState.stocks[symbol];
        
        // Refresh stocks page
        renderStocksPage();
        
        // Show notification
        showNotification(`Η μετοχή ${stockName} (${symbol}) αφαιρέθηκε επιτυχώς!`, 'success');
    }
}

// Refresh stock
function refreshStock(symbol) {
    fetchData(API_ENDPOINTS.stock(symbol), (response) => {
        if (response.status === 'success') {
            appState.stocks[symbol] = response.data;
            
            // Refresh stocks page
            renderStocksPage();
            
            // Update ticker if needed
            updateStockTicker();
            
            // Show notification
            showNotification(`Τα δεδομένα της μετοχής ${appState.stocks[symbol].name} (${symbol}) ενημερώθηκαν επιτυχώς!`, 'success');
        } else {
            showNotification(`Σφάλμα: ${response.message}`, 'error');
        }
    });
}

// Edit stock alert
function editStockAlert(symbol) {
    const stock = appState.stocks[symbol];
    if (!stock) return;
    
    // Create a modal for editing the alert threshold
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Επεξεργασία Ορίου Ειδοποίησης</h3>
                <span class="close-modal">&times;</span>
            </div>
            <div class="modal-body">
                <form id="edit-alert-form">
                    <div class="form-group">
                        <label for="alert-threshold">Όριο Ειδοποίησης για ${stock.name} (${symbol})</label>
                        <input type="number" id="alert-threshold" value="${stock.threshold || ''}" placeholder="π.χ. 18.50" step="0.01">
                    </div>
                    <div class="form-actions">
                        <button type="button" class="cancel-button">Ακύρωση</button>
                        <button type="submit" class="submit-button">Αποθήκευση</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add event listeners
    const closeButton = modal.querySelector('.close-modal');
    const cancelButton = modal.querySelector('.cancel-button');
    const form = modal.querySelector('#edit-alert-form');
    
    closeButton.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    cancelButton.addEventListener('click', () => {
        document.body.removeChild(modal);
    });
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const threshold = parseFloat(document.getElementById('alert-threshold').value) || null;
        
        // Call API to set alert threshold
        const data = {
            symbol: symbol,
            threshold: threshold
        };
        
        fetchData(API_ENDPOINTS.setAlert, (response) => {
            if (response.status === 'success') {
                // Update local state
                appState.stocks[symbol].threshold = threshold;
                
                // Refresh stocks page
                renderStocksPage();
                
                // Remove modal
                document.body.removeChild(modal);
                
                // Show notification
                showNotification(`Το όριο ειδοποίησης για τη μετοχή ${stock.name} (${symbol}) ορίστηκε επιτυχώς!`, 'success');
            } else {
                showNotification(`Σφάλμα: ${response.message}`, 'error');
            }
        }, 'POST', data);
    });
}

// View project logs
function viewProjectLogs(projectId) {
    const project = appState.projects[projectId];
    if (!project) return;
    
    // Get project logs
    const logs = project.logs || [];
    
    // Create a modal for viewing logs
    const modal = document.getElementById('project-details-modal');
    if (!modal) return;
    
    const modalTitle = document.getElementById('project-modal-title');
    const modalContent = document.getElementById('project-modal-content');
    
    if (modalTitle) {
        modalTitle.textContent = `Logs για ${project.name}`;
    }
    
    if (modalContent) {
        let html = '<div class="project-logs">';
        
        if (logs.length === 0) {
            html += '<div class="no-data">Δεν υπάρχουν διαθέσιμα logs.</div>';
        } else {
            html += '<ul class="logs-list">';
            logs.forEach((log, index) => {
                html += `<li class="log-item">${index + 1}. ${log}</li>`;
            });
            html += '</ul>';
        }
        
        html += '</div>';
        
        modalContent.innerHTML = html;
    }
    
    modal.classList.add('active');
}

// View project details
function viewProjectDetails(projectId) {
    const project = appState.projects[projectId];
    if (!project) return;
    
    // Create a modal for viewing project details
    const modal = document.getElementById('project-details-modal');
    if (!modal) return;
    
    const modalTitle = document.getElementById('project-modal-title');
    const modalContent = document.getElementById('project-modal-content');
    
    if (modalTitle) {
        modalTitle.textContent = `Λεπτομέρειες για ${project.name}`;
    }
    
    if (modalContent) {
        const statusClass = project.status === 'Active' ? 'active' : project.status === 'In Development' ? 'development' : 'planning';
        
        let html = `
            <div class="project-details">
                <div class="detail-item">
                    <div class="detail-label">Κατάσταση:</div>
                    <div class="detail-value">
                        <span class="status-indicator ${statusClass}"></span>
                        ${project.status}
                    </div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Περιγραφή:</div>
                    <div class="detail-value">${project.description}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Τελευταία ενημέρωση:</div>
                    <div class="detail-value">${project.last_update}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Πρόοδος:</div>
                    <div class="detail-value">
                        <div class="progress-bar">
                            <div class="progress-value" style="width: ${project.metrics.progress}%"></div>
                        </div>
                        <div class="progress-text">${project.metrics.progress}%</div>
                    </div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Μετρήσεις:</div>
                    <div class="detail-value">
                        <div class="metrics-grid">
        `;
        
        // Add project-specific metrics
        if (projectId === 'bidprice') {
            html += `
                <div class="metric-item">
                    <div class="metric-label">Ενεργές αγγελίες:</div>
                    <div class="metric-value">${project.metrics.active_listings}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Νέες προσφορές:</div>
                    <div class="metric-value">${project.metrics.new_bids}</div>
                </div>
            `;
        } else if (projectId === 'amesis') {
            html += `
                <div class="metric-item">
                    <div class="metric-label">Μηνύματα που στάλθηκαν:</div>
                    <div class="metric-value">${project.metrics.messages_sent}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Παραλήπτες:</div>
                    <div class="metric-value">${project.metrics.recipients}</div>
                </div>
            `;
        } else if (projectId === '6225') {
            html += `
                <div class="metric-item">
                    <div class="metric-label">Προϊόντα:</div>
                    <div class="metric-value">${project.metrics.products}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Πωλήσεις:</div>
                    <div class="metric-value">${project.metrics.sales}</div>
                </div>
            `;
        }
        
        html += `
                        </div>
                    </div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Πρόσφατα Logs:</div>
                    <div class="detail-value">
                        <ul class="logs-list">
        `;
        
        // Add the last 5 logs
        const logs = project.logs || [];
        const recentLogs = logs.slice(-5);
        
        if (recentLogs.length === 0) {
            html += '<li class="no-data">Δεν υπάρχουν διαθέσιμα logs.</li>';
        } else {
            recentLogs.forEach(log => {
                html += `<li class="log-item">${log}</li>`;
            });
        }
        
        html += `
                        </ul>
                        <button class="view-all-logs" data-project="${projectId}">Προβολή όλων των logs</button>
                    </div>
                </div>
            </div>
        `;
        
        modalContent.innerHTML = html;
        
        // Add event listener for view all logs button
        const viewAllLogsButton = modalContent.querySelector('.view-all-logs');
        if (viewAllLogsButton) {
            viewAllLogsButton.addEventListener('click', () => {
                viewProjectLogs(projectId);
            });
        }
    }
    
    modal.classList.add('active');
}

// Dismiss alert
function dismissAlert(index) {
    // In a real implementation, you would call an API endpoint to dismiss the alert
    // For now, just remove it from the local state
    if (index >= 0 && index < appState.alerts.length) {
        appState.alerts.splice(index, 1);
        
        // Refresh alerts page
        renderAlertsPage();
        
        // Update notification count
        const notificationCount = document.querySelector('.notification-count');
        if (notificationCount) {
            notificationCount.textContent = appState.alerts.length;
        }
        
        // Show notification
        showNotification('Η ειδοποίηση αποδέχθηκε επιτυχώς!', 'success');
    }
}

// Delete alert
function deleteAlert(index) {
    // In a real implementation, you would call an API endpoint to delete the alert
    // For now, just remove it from the local state
    if (index >= 0 && index < appState.alerts.length) {
        appState.alerts.splice(index, 1);
        
        // Refresh alerts page
        renderAlertsPage();
        
        // Update notification count
        const notificationCount = document.querySelector('.notification-count');
        if (notificationCount) {
            notificationCount.textContent = appState.alerts.length;
        }
        
        // Show notification
        showNotification('Η ειδοποίηση διαγράφηκε επιτυχώς!', 'success');
    }
}

// Send broadcast message
function sendBroadcast(message) {
    // In a real implementation, you would call an API endpoint to send the broadcast
    // For now, just show a notification
    
    // Close modal
    if (sendBroadcastModal) {
        sendBroadcastModal.classList.remove('active');
    }
    
    // Reset form
    if (broadcastForm) {
        broadcastForm.reset();
    }
    
    // Show notification
    showNotification('Το broadcast μήνυμα στάλθηκε επιτυχώς!', 'success');
}

// Update bot token
function updateBotToken(newToken) {
    // In a real implementation, you would call an API endpoint to update the token
    // For now, just show a notification
    
    // Close modal
    if (updateTokenModal) {
        updateTokenModal.classList.remove('active');
    }
    
    // Reset form
    if (updateTokenForm) {
        updateTokenForm.reset();
    }
    
    // Show notification
    showNotification('Το token του bot ενημερώθηκε επιτυχώς!', 'success');
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-message">${message}</div>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Add event listener for close button
    const closeButton = notification.querySelector('.notification-close');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            document.body.removeChild(notification);
        });
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (document.body.contains(notification)) {
            document.body.removeChild(notification);
        }
    }, 5000);
}

// Fetch data from API
function fetchData(endpoint, callback, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    fetch(endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            callback(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            showNotification(`Σφάλμα: ${error.message}`, 'error');
        });
}
