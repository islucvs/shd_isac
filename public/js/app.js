/**
 * Main Application Module
 * Division Agent Progress Tracker
 * Entry point and router
 */

import { PlayerAPI, MissionsAPI } from './api.js';
import { toast, modal, loading, updateTimeDisplay, debounce } from './ui.js';
import { 
    loadPlayer, 
    savePlayer, 
    getPlayer, 
    updateTopBar, 
    renderPlayerCard, 
    renderPlayerForm,
    getRecommendedMission,
    getCompletionPercentage
} from './player.js';
import { 
    loadMissions, 
    renderMissionCards, 
    renderFilterBar, 
    renderRecommendedMission,
    renderTimeline,
    renderStatistics,
    refreshMissionsView,
    openMissionModal
} from './missions.js';
import { openCreateMissionModal, openEditMissionModal, openDeleteModal } from './modal.js';

/**
 * Application State
 */
let currentPage = 'dashboard';
let missions = [];
let player = null;
let animationsEnabled = true;
let darkMode = true;

/**
 * Initialize Application
 */
async function init() {
    // Show loading screen
    loading.setProgress(20);
    
    // Initialize time display
    updateTimeDisplay();
    setInterval(updateTimeDisplay, 0);
    
    loading.setProgress(0);
    
    // Load data
    try {
        player = await loadPlayer();
        loading.setProgress(60);
        
        missions = await loadMissions();
        loading.setProgress(80);
        
        // Update UI
        updateTopBar();
        setupNavigation();
        setupKeyboardShortcuts();
        setupSearch();
        
        loading.setProgress(100);
        
        // Hide loading screen
        setTimeout(() => {
            loading.hide();
            navigateTo('dashboard');
        }, 3000);
        
    } catch (error) {
        console.error('Initialization error:', error);
        toast.error('Failed to initialize application', 'CRITICAL ERROR');
        loading.hide();
    }
}

/**
 * Setup Navigation
 */
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            if (page) {
                navigateTo(page);
            }
        });
    });
    
    // Mobile navigation
    const mobileNavItems = document.querySelectorAll('.mobile-nav-item');
    mobileNavItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            if (page) {
                navigateTo(page);
            }
        });
    });
}

/**
 * Navigate to page
 */
function navigateTo(page) {
    currentPage = page;
    
    // Update active nav
    document.querySelectorAll('.nav-item, .mobile-nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });
    
    // Render page content
    const mainContent = document.getElementById('main-content');
    if (!mainContent) return;
    
    switch (page) {
        case 'dashboard':
            renderDashboard(mainContent);
            break;
        case 'missions':
            renderMissions(mainContent);
            break;
        case 'timeline':
            renderTimelinePage(mainContent);
            break;
        case 'player':
            renderPlayerPage(mainContent);
            break;
        case 'statistics':
            renderStatisticsPage(mainContent);
            break;
        case 'settings':
            renderSettingsPage(mainContent);
            break;
        default:
            renderDashboard(mainContent);
    }
    
    // Update right panel
    updateRightPanel();
}

/**
 * Render Dashboard
 */
function renderDashboard(container) {
    const completionPercent = getCompletionPercentage(missions);
    const recommended = getRecommendedMission(missions);
    
    container.innerHTML = `
        <h2 class="page-title">DASHBOARD</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-lg);">
            <div id="dashboard-player-card"></div>
            <div id="dashboard-recommended"></div>
        </div>
        <div class="card animate-fade-in-up stagger-3" style="margin-top: var(--spacing-lg);">
            <div class="card-header">
                <div class="card-title">MISSION PROGRESS</div>
            </div>
            <div class="card-body">
                <div class="progress-label">
                    <span>Overall Completion</span>
                    <span class="progress-value">${completionPercent}%</span>
                </div>
                <div class="progress-container" style="margin-bottom: var(--spacing-lg);">
                    <div class="progress-bar" style="width: ${completionPercent}%"></div>
                </div>
                <div class="stat-grid" style="grid-template-columns: repeat(4, 1fr);">
                    <div class="stat-item">
                        <span class="stat-value">${missions.filter(m => m.completed).length}</span>
                        <span class="stat-label">Completed</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${missions.filter(m => !m.completed).length}</span>
                        <span class="stat-label">Pending</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${missions.length}</span>
                        <span class="stat-label">Total</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${recommended ? recommended.level : 'N/A'}</span>
                        <span class="stat-label">Next Level</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Render player card
    const playerCardContainer = document.getElementById('dashboard-player-card');
    if (playerCardContainer) {
        renderPlayerCard(playerCardContainer);
    }
    
    // Render recommended mission
    const recommendedContainer = document.getElementById('dashboard-recommended');
    if (recommendedContainer) {
        renderRecommendedMission(recommendedContainer);
    }
}

/**
 * Render Missions Page
 */
function renderMissions(container) {
    container.innerHTML = `
        <h2 class="page-title">MISSIONS</h2>
        <div id="missions-filter-bar"></div>
        <div id="missions-grid" class="mission-grid"></div>
    `;
    
    const filterBar = document.getElementById('missions-filter-bar');
    const missionsGrid = document.getElementById('missions-grid');
    
    if (filterBar) {
        renderFilterBar(filterBar, () => {
            refreshMissionsView();
        });
    }
    
    if (missionsGrid) {
        renderMissionCards(missionsGrid, missions);
    }
}

/**
 * Render Timeline Page
 */
function renderTimelinePage(container) {
    container.innerHTML = `
        <h2 class="page-title">TIMELINE</h2>
        <div id="timeline-container"></div>
    `;
    
    const timelineContainer = document.getElementById('timeline-container');
    if (timelineContainer) {
        renderTimeline(timelineContainer);
    }
}

/**
 * Render Player Page
 */
function renderPlayerPage(container) {
    container.innerHTML = `
        <h2 class="page-title">AGENT PROFILE</h2>
        <div style="max-width: 600px;">
            <div id="player-form-container"></div>
        </div>
    `;
    
    const formContainer = document.getElementById('player-form-container');
    if (formContainer) {
        renderPlayerForm(formContainer, (updatedPlayer) => {
            player = updatedPlayer;
            updateTopBar();
        });
    }
}

/**
 * Render Statistics Page
 */
function renderStatisticsPage(container) {
    container.innerHTML = `
        <h2 class="page-title">STATISTICS</h2>
        <div id="statistics-container"></div>
    `;
    
    const statsContainer = document.getElementById('statistics-container');
    if (statsContainer) {
        renderStatistics(statsContainer);
    }
}

/**
 * Render Settings Page
 */
function renderSettingsPage(container) {
    container.innerHTML = `
        <h2 class="page-title">SETTINGS</h2>
        
        <div class="settings-section animate-fade-in-up">
            <div class="settings-section-title">Interface</div>
            <div class="setting-item">
                <div class="setting-item-info">
                    <h4>Dark Mode</h4>
                    <p>Enable dark theme interface</p>
                </div>
                <div class="toggle-switch ${darkMode ? 'active' : ''}" id="toggle-darkmode"></div>
            </div>
            <div class="setting-item">
                <div class="setting-item-info">
                    <h4>Animations</h4>
                    <p>Enable UI animations and effects</p>
                </div>
                <div class="toggle-switch ${animationsEnabled ? 'active' : ''}" id="toggle-animations"></div>
            </div>
        </div>
        
        <div class="settings-section animate-fade-in-up stagger-2">
            <div class="settings-section-title">Data Management</div>
            <div class="setting-item">
                <div class="setting-item-info">
                    <h4>Reset Progress</h4>
                    <p>Reset all mission progress to default</p>
                </div>
                <button class="btn btn-danger" id="reset-progress-btn">RESET</button>
            </div>
            <div class="setting-item">
                <div class="setting-item-info">
                    <h4>Export Data</h4>
                    <p>Download all data as JSON file</p>
                </div>
                <button class="btn" id="export-data-btn">EXPORT</button>
            </div>
            <div class="setting-item">
                <div class="setting-item-info">
                    <h4>Import Data</h4>
                    <p>Import data from JSON file</p>
                </div>
                <button class="btn" id="import-data-btn">IMPORT</button>
                <input type="file" id="import-file-input" accept=".json" style="display: none;">
            </div>
        </div>
    `;
    
    // Toggle dark mode
    document.getElementById('toggle-darkmode')?.addEventListener('click', function() {
        darkMode = !darkMode;
        this.classList.toggle('active');
        toast.info(`Dark mode ${darkMode ? 'enabled' : 'disabled'}`, 'SETTING UPDATED');
    });
    
    // Toggle animations
    document.getElementById('toggle-animations')?.addEventListener('click', function() {
        animationsEnabled = !animationsEnabled;
        this.classList.toggle('active');
        document.body.classList.toggle('reduce-motion', !animationsEnabled);
        toast.info(`Animations ${animationsEnabled ? 'enabled' : 'disabled'}`, 'SETTING UPDATED');
    });
    
    // Reset progress
    document.getElementById('reset-progress-btn')?.addEventListener('click', async () => {
        const confirmed = await modal.confirm(
            'This will reset all mission progress. Are you sure?',
            'RESET PROGRESS'
        );
        
        if (confirmed) {
            try {
                // Reset all missions to not completed
                const resetPromises = missions.map(mission => 
                    MissionsAPI.update(mission.id, { completed: false })
                );
                await Promise.all(resetPromises);
                
                // Reload missions
                missions = await loadMissions();
                toast.success('Progress reset successfully', 'RESET COMPLETE');
                
                if (currentPage === 'dashboard') {
                    renderDashboard(container);
                }
            } catch (error) {
                toast.error('Failed to reset progress', 'ERROR');
            }
        }
    });
    
    // Export data
    document.getElementById('export-data-btn')?.addEventListener('click', async () => {
        try {
            const data = {
                player: await PlayerAPI.get(),
                missions: await MissionsAPI.getAll(),
                exportDate: new Date().toISOString()
            };
            
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `division-tracker-backup-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            toast.success('Data exported successfully', 'EXPORT COMPLETE');
        } catch (error) {
            toast.error('Failed to export data', 'ERROR');
        }
    });
    
    // Import data
    document.getElementById('import-data-btn')?.addEventListener('click', () => {
        document.getElementById('import-file-input')?.click();
    });
    
    document.getElementById('import-file-input')?.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        try {
            const text = await file.text();
            const data = JSON.parse(text);
            
            if (data.player) {
                await PlayerAPI.update(data.player);
            }
            
            if (data.missions && Array.isArray(data.missions)) {
                // Clear existing missions and import new ones
                const existingMissions = await MissionsAPI.getAll();
                for (const mission of existingMissions) {
                    await MissionsAPI.delete(mission.id);
                }
                
                for (const mission of data.missions) {
                    const { id, ...missionData } = mission;
                    await MissionsAPI.create(missionData);
                }
            }
            
            // Reload data
            player = await loadPlayer();
            missions = await loadMissions();
            updateTopBar();
            
            toast.success('Data imported successfully', 'IMPORT COMPLETE');
            
            if (currentPage === 'dashboard') {
                renderDashboard(container);
            }
        } catch (error) {
            toast.error('Failed to import data. Invalid file format.', 'ERROR');
        }
        
        // Reset file input
        e.target.value = '';
    });
}

/**
 * Update Right Panel
 */
function updateRightPanel() {
    const rightPanel = document.getElementById('right-panel');
    if (!rightPanel) return;
    
    const completed = missions.filter(m => m.completed).length;
    const pending = missions.length - completed;
    const completionPercent = missions.length > 0 ? Math.round((completed / missions.length) * 100) : 0;
    
    rightPanel.innerHTML = `
        <div class="panel-section">
            <div class="panel-section-title">AGENT STATUS</div>
            <div class="stat-grid" style="grid-template-columns: 1fr 1fr;">
                <div class="stat-item" style="padding: var(--spacing-sm);">
                    <span class="stat-value" style="font-size: 1.1rem;">${player ? player.level : '-'}</span>
                    <span class="stat-label" style="font-size: 0.65rem;">Level</span>
                </div>
                <div class="stat-item" style="padding: var(--spacing-sm);">
                    <span class="stat-value" style="font-size: 1.1rem;">${player ? player.district : '-'}</span>
                    <span class="stat-label" style="font-size: 0.65rem;">District</span>
                </div>
            </div>
        </div>
        
        <div class="panel-section">
            <div class="panel-section-title">MISSION STATUS</div>
            <div class="stat-grid" style="grid-template-columns: 1fr 1fr;">
                <div class="stat-item" style="padding: var(--spacing-sm);">
                    <span class="stat-value" style="font-size: 1.1rem;">${completed}</span>
                    <span class="stat-label" style="font-size: 0.65rem;">Completed</span>
                </div>
                <div class="stat-item" style="padding: var(--spacing-sm);">
                    <span class="stat-value" style="font-size: 1.1rem;">${pending}</span>
                    <span class="stat-label" style="font-size: 0.65rem;">Pending</span>
                </div>
            </div>
            <div style="margin-top: var(--spacing-md);">
                <div class="progress-label">
                    <span style="font-size: 0.75rem;">Completion</span>
                    <span class="progress-value" style="font-size: 0.75rem;">${completionPercent}%</span>
                </div>
                <div class="progress-container" style="height: 6px;">
                    <div class="progress-bar" style="width: ${completionPercent}%"></div>
                </div>
            </div>
        </div>
        
        <div class="panel-section">
            <div class="panel-section-title">QUICK ACTIONS</div>
            <div style="display: flex; flex-direction: column; gap: var(--spacing-sm);">
                <button class="btn btn-sm" id="quick-new-mission" style="justify-content: flex-start;">
                    <span>+</span> New Mission
                </button>
                <button class="btn btn-sm" id="quick-view-missions" style="justify-content: flex-start;">
                    <span>LIST_ICON</span> View Missions
                </button>
                <button class="btn btn-sm" id="quick-player" style="justify-content: flex-start;">
                    <span>PERSON_ICON</span> Edit Profile
                </button>
            </div>
        </div>
    `;
    
    // Quick action handlers
    document.getElementById('quick-new-mission')?.addEventListener('click', () => {
        openCreateMissionModal();
    });
    
    document.getElementById('quick-view-missions')?.addEventListener('click', () => {
        navigateTo('missions');
    });
    
    document.getElementById('quick-player')?.addEventListener('click', () => {
        navigateTo('player');
    });
}

/**
 * Setup Keyboard Shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl+N - New Mission
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            if (currentPage === 'missions') {
                openCreateMissionModal();
            }
        }
        
        // Ctrl+S - Save Player
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            if (currentPage === 'player') {
                const form = document.getElementById('player-form');
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
            }
        }
        
        // ESC - Close modal
        if (e.key === 'Escape') {
            modal.close();
        }
    });
}

/**
 * Setup Search
 */
function setupSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            const query = e.target.value.toLowerCase();
            if (currentPage === 'missions') {
                const missionsGrid = document.getElementById('missions-grid');
                if (missionsGrid) {
                    const filtered = missions.filter(m => 
                        m.name.toLowerCase().includes(query) || 
                        m.district.toLowerCase().includes(query)
                    );
                    renderMissionCards(missionsGrid, filtered);
                }
            }
        }, 300));
    }
}

/**
 * Refresh all data
 */
async function refreshData() {
    player = await loadPlayer();
    missions = await loadMissions();
    updateTopBar();
    updateRightPanel();
    
    if (currentPage === 'dashboard') {
        const mainContent = document.getElementById('main-content');
        if (mainContent) renderDashboard(mainContent);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);

// Export for global access
window.DivisionTracker = {
    navigateTo,
    refreshData,
    getCurrentPage: () => currentPage
};
