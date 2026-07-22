/**
 * Player Module
 * Handles player data, stats, and auto-recommendation engine
 */

import { PlayerAPI, MissionsAPI } from './api.js';
import { toast, formatNumber } from './ui.js';

/**
 * Player State
 */
let playerData = null;

/**
 * Load player data from API
 */
async function loadPlayer() {
    try {
        playerData = await PlayerAPI.get();
        return playerData;
    } catch (error) {
        toast.error('Failed to load agent data', 'SYSTEM ERROR');
        console.error('Player load error:', error);
        return null;
    }
}

/**
 * Save player data to API
 */
async function savePlayer(data) {
    try {
        playerData = await PlayerAPI.update(data);
        toast.success('Agent data updated successfully', 'DATA SAVED');
        return playerData;
    } catch (error) {
        toast.error('Failed to save agent data', 'SYSTEM ERROR');
        console.error('Player save error:', error);
        return null;
    }
}

/**
 * Get current player data
 */
function getPlayer() {
    return playerData;
}

/**
 * Calculate XP needed for next level
 * Division-style progression
 */
function getXpForLevel(level) {
    return Math.floor(1000 * Math.pow(level, 1.5));
}

/**
 * Calculate XP progress percentage
 */
function getXpProgress() {
    if (!playerData) return 0;
    const currentLevelXp = getXpForLevel(playerData.level);
    const nextLevelXp = getXpForLevel(playerData.level + 1);
    const xpInLevel = playerData.xp - currentLevelXp;
    const xpNeeded = nextLevelXp - currentLevelXp;
    return Math.min(100, Math.max(0, (xpInLevel / xpNeeded) * 100));
}

/**
 * Calculate overall completion percentage
 */
function getCompletionPercentage(missions) {
    if (!missions || missions.length === 0) return 0;
    const completed = missions.filter(m => m.completed).length;
    return Math.round((completed / missions.length) * 100);
}

/**
 * Auto Recommendation Engine
 * Recommends the best mission based on:
 * 1. Highest priority
 * 2. Not completed
 * 3. Player level >= mission level - 1
 * 4. Lowest required level if multiple exist
 */
function getRecommendedMission(missions) {
    if (!playerData || !missions) return null;
    
    const eligibleMissions = missions.filter(mission => {
        return !mission.completed && playerData.level >= mission.level - 1;
    });
    
    if (eligibleMissions.length === 0) return null;
    
    // Sort by priority (desc), then by level (asc)
    eligibleMissions.sort((a, b) => {
        if (b.priority !== a.priority) {
            return b.priority - a.priority;
        }
        return a.level - b.level;
    });
    
    return eligibleMissions[0];
}

/**
 * Calculate average mission level
 */
function getAverageMissionLevel(missions) {
    if (!missions || missions.length === 0) return 0;
    const total = missions.reduce((sum, m) => sum + m.level, 0);
    return Math.round(total / missions.length);
}

/**
 * Calculate average difficulty
 */
function getAverageDifficulty(missions) {
    if (!missions || missions.length === 0) return 0;
    const total = missions.reduce((sum, m) => sum + m.difficulty, 0);
    return (total / missions.length).toFixed(1);
}

/**
 * Get current priority mission (highest priority, not completed)
 */
function getCurrentPriorityMission(missions) {
    if (!missions) return null;
    const pending = missions.filter(m => !m.completed);
    if (pending.length === 0) return null;
    return pending.reduce((highest, m) => m.priority > highest.priority ? m : highest, pending[0]);
}

/**
 * Render player card for dashboard
 */
function renderPlayerCard(container) {
    if (!playerData) return;
    
    const xpProgress = getXpProgress();
    
    container.innerHTML = `
        <div class="player-card animate-fade-in-up">
            <div class="player-card-header">
                <div class="player-avatar">${playerData.name.charAt(0).toUpperCase()}</div>
                <div class="player-info">
                    <h2>${playerData.name}</h2>
                    <div class="player-level">LEVEL ${playerData.level}</div>
                </div>
            </div>
            <div class="player-stats">
                <div class="player-stat">
                    <div class="player-stat-label">Primary DPS</div>
                    <div class="player-stat-value">${formatNumber(playerData.firepower)}</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-label">Toughness</div>
                    <div class="player-stat-value">${formatNumber(playerData.toughness)}</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-label">Skill Power</div>
                    <div class="player-stat-value">${formatNumber(playerData.skillPower)}</div>
                </div>
            </div>
            <div class="progress-container" style="margin-bottom: var(--spacing-xs);">
                <div class="progress-bar" style="width: ${xpProgress}%"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--color-text-secondary);">
                <span>XP Progress</span>
                <span style="color: var(--color-accent-primary);">${Math.round(xpProgress)}%</span>
            </div>
        </div>
    `;
}

/**
 * Render player edit form
 */
function renderPlayerForm(container, onSave) {
    if (!playerData) return;
    
    container.innerHTML = `
        <form id="player-form" class="animate-fade-in-up">
            <div class="form-group">
                <label class="form-label">Agent Name</label>
                <input type="text" class="form-input" id="player-name" value="${playerData.name}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Level</label>
                <input type="number" class="form-input" id="player-level" value="${playerData.level}" min="1" max="30" required>
            </div>
            <div class="form-group">
                <label class="form-label">Firepower</label>
                <input type="number" class="form-input" id="player-firepower" value="${playerData.firepower}" min="0" required>
            </div>
            <div class="form-group">
                <label class="form-label">Toughness</label>
                <input type="number" class="form-input" id="player-toughness" value="${playerData.toughness}" min="0" required>
            </div>
            <div class="form-group">
                <label class="form-label">Skill Power</label>
                <input type="number" class="form-input" id="player-skillpower" value="${playerData.skillPower}" min="0" required>
            </div>
            <div class="form-group">
                <label class="form-label">Current District</label>
                <input type="text" class="form-input" id="player-district" value="${playerData.district}" required>
            </div>
            <div class="form-group">
                <label class="form-label">XP</label>
                <input type="number" class="form-input" id="player-xp" value="${playerData.xp}" min="0" required>
            </div>
            <div class="btn-group">
                <button type="submit" class="btn btn-primary">SAVE CHANGES</button>
            </div>
        </form>
    `;
    
    const form = container.querySelector('#player-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const updatedData = {
            name: document.getElementById('player-name').value,
            level: parseInt(document.getElementById('player-level').value),
            firepower: parseInt(document.getElementById('player-firepower').value),
            toughness: parseInt(document.getElementById('player-toughness').value),
            skillPower: parseInt(document.getElementById('player-skillpower').value),
            district: document.getElementById('player-district').value,
            xp: parseInt(document.getElementById('player-xp').value)
        };
        
        const result = await savePlayer(updatedData);
        if (result && onSave) {
            onSave(result);
        }
    });
}

/**
 * Update top bar with player info
 */
function updateTopBar() {
    if (!playerData) return;
    
    const nameEl = document.querySelector('.agent-name');
    const levelEl = document.querySelector('.agent-level');
    const districtEl = document.querySelector('.agent-district');
    
    if (nameEl) nameEl.textContent = playerData.name;
    if (levelEl) levelEl.textContent = `LV.${playerData.level}`;
    if (districtEl) districtEl.textContent = playerData.district;
}

export {
    loadPlayer,
    savePlayer,
    getPlayer,
    getXpForLevel,
    getXpProgress,
    getCompletionPercentage,
    getRecommendedMission,
    getAverageMissionLevel,
    getAverageDifficulty,
    getCurrentPriorityMission,
    renderPlayerCard,
    renderPlayerForm,
    updateTopBar
};
