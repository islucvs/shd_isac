/**
 * Missions Module
 * Handles mission CRUD operations, filtering, sorting, and rendering
 */

import { MissionsAPI } from './api.js';
import { toast, modal, formatNumber, escapeHtml } from './ui.js';
import { getPlayer, getRecommendedMission } from './player.js';

/**
 * Mission State
 */
let missions = [];
let currentFilter = 'all';
let currentSort = 'level';
let searchQuery = '';

/**
 * Load all missions
 */
async function loadMissions() {
    try {
        missions = await MissionsAPI.getAll();
        return missions;
    } catch (error) {
        toast.error('Failed to load mission data', 'SYSTEM ERROR');
        console.error('Missions load error:', error);
        return [];
    }
}

/**
 * Get all missions
 */
function getMissions() {
    return missions;
}

/**
 * Get mission by ID
 */
function getMissionById(id) {
    return missions.find(m => m.id === id);
}

/**
 * Create new mission
 */
async function createMission(missionData) {
    try {
        const newMission = await MissionsAPI.create(missionData);
        missions.push(newMission);
        toast.success(`Mission "${newMission.name}" created`, 'MISSION ADDED');
        return newMission;
    } catch (error) {
        toast.error('Failed to create mission', 'SYSTEM ERROR');
        console.error('Create mission error:', error);
        return null;
    }
}

/**
 * Update mission
 */
async function updateMission(id, missionData) {
    try {
        const updated = await MissionsAPI.update(id, missionData);
        const index = missions.findIndex(m => m.id === id);
        if (index !== -1) {
            missions[index] = updated;
        }
        toast.success(`Mission "${updated.name}" updated`, 'MISSION UPDATED');
        return updated;
    } catch (error) {
        toast.error('Failed to update mission', 'SYSTEM ERROR');
        console.error('Update mission error:', error);
        return null;
    }
}

/**
 * Delete mission
 */
async function deleteMission(id) {
    try {
        const mission = missions.find(m => m.id === id);
        const confirmed = await modal.confirm(
            `Are you sure you want to delete mission "${mission ? mission.name : ''}"? This action cannot be undone.`,
            'DELETE MISSION'
        );
        
        if (!confirmed) return false;
        
        await MissionsAPI.delete(id);
        missions = missions.filter(m => m.id !== id);
        toast.success('Mission deleted', 'MISSION REMOVED');
        return true;
    } catch (error) {
        toast.error('Failed to delete mission', 'SYSTEM ERROR');
        console.error('Delete mission error:', error);
        return false;
    }
}

/**
 * Toggle mission completion
 */
async function toggleMissionComplete(id) {
    const mission = missions.find(m => m.id === id);
    if (!mission) return null;
    
    const updated = await updateMission(id, { completed: !mission.completed });
    if (updated) {
        if (updated.completed) {
            toast.success(`Mission "${updated.name}" completed!`, 'MISSION COMPLETE');
        } else {
            toast.info(`Mission "${updated.name}" marked as pending`, 'STATUS UPDATED');
        }
    }
    return updated;
}

/**
 * Filter missions
 */
function filterMissions(filter = currentFilter, search = searchQuery) {
    let filtered = [...missions];
    
    // Search filter
    if (search) {
        const query = search.toLowerCase();
        filtered = filtered.filter(m => 
            m.name.toLowerCase().includes(query) || 
            m.district.toLowerCase().includes(query)
        );
    }
    
    // Status filter
    if (filter === 'completed') {
        filtered = filtered.filter(m => m.completed);
    } else if (filter === 'pending') {
        filtered = filtered.filter(m => !m.completed);
    }
    
    return filtered;
}

/**
 * Sort missions
 */
function sortMissions(missionsToSort, sortBy = currentSort) {
    const sorted = [...missionsToSort];
    
    switch (sortBy) {
        case 'level':
            sorted.sort((a, b) => a.level - b.level);
            break;
        case 'xp':
            sorted.sort((a, b) => b.xp - a.xp);
            break;
        case 'priority':
            sorted.sort((a, b) => b.priority - a.priority);
            break;
        case 'difficulty':
            sorted.sort((a, b) => b.difficulty - a.difficulty);
            break;
        case 'alphabetical':
            sorted.sort((a, b) => a.name.localeCompare(b.name));
            break;
        default:
            sorted.sort((a, b) => a.level - b.level);
    }
    
    return sorted;
}

/**
 * Get unique districts
 */
function getDistricts() {
    const districts = new Set(missions.map(m => m.district));
    return Array.from(districts).sort();
}

/**
 * Render difficulty stars
 */
function renderDifficultyStars(difficulty) {
    let stars = '';
    for (let i = 1; i <= 5; i++) {
        stars += `<span class="difficulty-star ${i <= difficulty ? 'active' : ''}">STAR</span>`;
    }
    return stars;
}

/**
 * Render mission cards
 */
function renderMissionCards(container, missionList) {
    if (!container) return;
    
    if (missionList.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">LIST_EMOJI</div>
                <div class="empty-state-title">NO MISSIONS FOUND</div>
                <div class="empty-state-text">No missions match your current filters.</div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = missionList.map((mission, index) => `
        <div class="mission-card ${mission.completed ? 'completed' : ''} animate-fade-in-up stagger-${Math.min(index + 1, 10)}" data-id="${mission.id}">
            <div class="mission-card-header">
                <div>
                    <div class="mission-card-title">${escapeHtml(mission.name)}</div>
                    <div class="card-subtitle">${escapeHtml(mission.district)}</div>
                </div>
                <div class="badge ${mission.completed ? 'badge-success' : 'badge-pending'}">
                    ${mission.completed ? 'COMPLETED' : 'PENDING'}
                </div>
            </div>
            <div class="mission-card-meta">
                <div class="mission-card-meta-item">
                    <span class="mission-card-meta-label">Level</span>
                    <span class="mission-card-meta-value">${mission.level}</span>
                </div>
                <div class="mission-card-meta-item">
                    <span class="mission-card-meta-label">XP</span>
                    <span class="mission-card-meta-value">${formatNumber(mission.xp)}</span>
                </div>
                <div class="mission-card-meta-item">
                    <span class="mission-card-meta-label">Difficulty</span>
                    <span class="mission-card-meta-value">
                        <div class="difficulty-stars">${renderDifficultyStars(mission.difficulty)}</div>
                    </span>
                </div>
                <div class="mission-card-meta-item">
                    <span class="mission-card-meta-label">Priority</span>
                    <span class="mission-card-meta-value">${mission.priority}/5</span>
                </div>
            </div>
            ${mission.notes ? `<div style="font-size: 0.85rem; color: var(--color-text-secondary); margin-bottom: var(--spacing-md); font-style: italic;">${escapeHtml(mission.notes)}</div>` : ''}
            <div class="mission-card-actions">
                <button class="btn btn-sm btn-success mission-complete-btn" data-id="${mission.id}">
                    ${mission.completed ? 'UNDO' : 'COMPLETE'}
                </button>
                <button class="btn btn-sm mission-edit-btn" data-id="${mission.id}">EDIT</button>
                <button class="btn btn-sm btn-danger mission-delete-btn" data-id="${mission.id}">DELETE</button>
            </div>
        </div>
    `).join('');
    
    // Attach event listeners
    container.querySelectorAll('.mission-complete-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const id = parseInt(e.target.dataset.id);
            await toggleMissionComplete(id);
            refreshMissionsView();
        });
    });
    
    container.querySelectorAll('.mission-edit-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.target.dataset.id);
            openMissionModal(id);
        });
    });
    
    container.querySelectorAll('.mission-delete-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const id = parseInt(e.target.dataset.id);
            await deleteMission(id);
            refreshMissionsView();
        });
    });
}

/**
 * Render filter bar
 */
function renderFilterBar(container, onFilterChange) {
    if (!container) return;
    
    const districts = getDistricts();
    
    container.innerHTML = `
        <div class="filter-group">
            <label>Status</label>
            <select class="form-select" id="filter-status" style="width: 120px;">
                <option value="all">All</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
            </select>
        </div>
        <div class="filter-group">
            <label>District</label>
            <select class="form-select" id="filter-district" style="width: 150px;">
                <option value="all">All Districts</option>
                ${districts.map(d => `<option value="${escapeHtml(d)}">${escapeHtml(d)}</option>`).join('')}
            </select>
        </div>
        <div class="filter-group">
            <label>Sort By</label>
            <select class="form-select" id="sort-by" style="width: 140px;">
                <option value="level">Level</option>
                <option value="xp">XP</option>
                <option value="priority">Priority</option>
                <option value="difficulty">Difficulty</option>
                <option value="alphabetical">Alphabetical</option>
            </select>
        </div>
        <div class="filter-group" style="margin-left: auto;">
            <button class="btn btn-primary" id="create-mission-btn">
                <span>+</span> NEW MISSION
            </button>
        </div>
    `;
    
    // Event listeners
    container.querySelector('#filter-status').addEventListener('change', (e) => {
        currentFilter = e.target.value;
        if (onFilterChange) onFilterChange();
    });
    
    container.querySelector('#filter-district').addEventListener('change', (e) => {
        const district = e.target.value;
        if (district === 'all') {
            currentFilter = 'all';
        } else {
            // Custom district filter logic
        }
        if (onFilterChange) onFilterChange();
    });
    
    container.querySelector('#sort-by').addEventListener('change', (e) => {
        currentSort = e.target.value;
        if (onFilterChange) onFilterChange();
    });
    
    container.querySelector('#create-mission-btn').addEventListener('click', () => {
        openMissionModal();
    });
}

/**
 * Refresh missions view
 */
function refreshMissionsView() {
    const container = document.getElementById('missions-grid');
    if (container) {
        let filtered = filterMissions();
        filtered = sortMissions(filtered);
        renderMissionCards(container, filtered);
    }
}

/**
 * Open mission modal (create/edit)
 */
function openMissionModal(missionId = null) {
    const isEdit = missionId !== null;
    const mission = isEdit ? getMissionById(missionId) : null;
    
    const content = document.createElement('div');
    content.innerHTML = `
        <h3 style="font-family: var(--font-display); font-size: 1.1rem; color: var(--color-accent-primary); margin-bottom: var(--spacing-lg); text-transform: uppercase; letter-spacing: 2px;">
            ${isEdit ? 'EDIT MISSION' : 'NEW MISSION'}
        </h3>
        <form id="mission-form">
            <div class="form-group">
                <label class="form-label">Mission Name</label>
                <input type="text" class="form-input" id="mission-name" value="${isEdit ? escapeHtml(mission.name) : ''}" required>
            </div>
            <div class="form-group">
                <label class="form-label">District</label>
                <input type="text" class="form-input" id="mission-district" value="${isEdit ? escapeHtml(mission.district) : ''}" required>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md);">
                <div class="form-group">
                    <label class="form-label">Required Level</label>
                    <input type="number" class="form-input" id="mission-level" value="${isEdit ? mission.level : '1'}" min="1" max="30" required>
                </div>
                <div class="form-group">
                    <label class="form-label">XP Reward</label>
                    <input type="number" class="form-input" id="mission-xp" value="${isEdit ? mission.xp : '0'}" min="0" required>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md);">
                <div class="form-group">
                    <label class="form-label">Difficulty (1-5)</label>
                    <input type="number" class="form-input" id="mission-difficulty" value="${isEdit ? mission.difficulty : '1'}" min="1" max="5" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Priority (1-5)</label>
                    <input type="number" class="form-input" id="mission-priority" value="${isEdit ? mission.priority : '1'}" min="1" max="5" required>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Notes</label>
                <textarea class="form-textarea" id="mission-notes" rows="3">${isEdit ? escapeHtml(mission.notes || '') : ''}</textarea>
            </div>
            <div class="btn-group" style="justify-content: flex-end;">
                <button type="button" class="btn" id="modal-cancel-btn">CANCEL</button>
                <button type="submit" class="btn btn-primary">${isEdit ? 'UPDATE' : 'CREATE'}</button>
            </div>
        </form>
    `;
    
    const modalContent = modal.open(content, { maxWidth: '500px' });
    
    modalContent.querySelector('#modal-cancel-btn').addEventListener('click', () => {
        modal.close();
    });
    
    modalContent.querySelector('#mission-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const missionData = {
            name: document.getElementById('mission-name').value,
            district: document.getElementById('mission-district').value,
            level: parseInt(document.getElementById('mission-level').value),
            xp: parseInt(document.getElementById('mission-xp').value),
            difficulty: parseInt(document.getElementById('mission-difficulty').value),
            priority: parseInt(document.getElementById('mission-priority').value),
            notes: document.getElementById('mission-notes').value
        };
        
        if (isEdit) {
            await updateMission(missionId, missionData);
        } else {
            await createMission(missionData);
        }
        
        modal.close();
        refreshMissionsView();
    });
}

/**
 * Render recommended mission card
 */
function renderRecommendedMission(container) {
    if (!container) return;
    
    const recommended = getRecommendedMission(missions);
    const player = getPlayer();
    
    if (!recommended) {
        container.innerHTML = `
            <div class="card animate-fade-in-up">
                <div class="card-header">
                    <div>
                        <div class="card-title">RECOMMENDED MISSION</div>
                        <div class="card-subtitle">No missions available</div>
                    </div>
                </div>
                <div class="card-body">
                    <p>All available missions have been completed or are above your current level.</p>
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="card animate-fade-in-up" style="border-color: rgba(255, 106, 0, 0.4);">
            <div class="card-header">
                <div>
                    <div class="card-title" style="color: var(--color-accent-primary);">RECOMMENDED MISSION</div>
                    <div class="card-subtitle">${escapeHtml(recommended.district)}</div>
                </div>
                <div class="badge badge-primary">PRIORITY ${recommended.priority}</div>
            </div>
            <div class="card-body">
                <h3 style="font-family: var(--font-display); font-size: 1.2rem; margin-bottom: var(--spacing-md); color: var(--color-text-primary);">${escapeHtml(recommended.name)}</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-md); margin-bottom: var(--spacing-md);">
                    <div class="stat-item" style="padding: var(--spacing-sm);">
                        <span class="stat-value" style="font-size: 1.1rem;">${recommended.level}</span>
                        <span class="stat-label" style="font-size: 0.65rem;">Level</span>
                    </div>
                    <div class="stat-item" style="padding: var(--spacing-sm);">
                        <span class="stat-value" style="font-size: 1.1rem;">${formatNumber(recommended.xp)}</span>
                        <span class="stat-label" style="font-size: 0.65rem;">XP</span>
                    </div>
                    <div class="stat-item" style="padding: var(--spacing-sm);">
                        <span class="stat-value" style="font-size: 1.1rem;">${recommended.difficulty}</span>
                        <span class="stat-label" style="font-size: 0.65rem;">Difficulty</span>
                    </div>
                </div>
                <div class="btn-group">
                    <button class="btn btn-primary mission-start-btn" data-id="${recommended.id}">START MISSION</button>
                    <button class="btn mission-edit-btn" data-id="${recommended.id}">EDIT</button>
                    <button class="btn btn-success mission-complete-btn" data-id="${recommended.id}">COMPLETE</button>
                </div>
            </div>
        </div>
    `;
    
    // Attach event listeners
    container.querySelector('.mission-start-btn')?.addEventListener('click', () => {
        toast.info(`Starting mission: ${recommended.name}`, 'MISSION STARTED');
    });
    
    container.querySelector('.mission-edit-btn')?.addEventListener('click', () => {
        openMissionModal(recommended.id);
    });
    
    container.querySelector('.mission-complete-btn')?.addEventListener('click', async () => {
        await toggleMissionComplete(recommended.id);
        refreshMissionsView();
        renderRecommendedMission(container);
    });
}

/**
 * Render timeline
 */
function renderTimeline(container) {
    if (!container) return;
    
    const sortedMissions = [...missions].sort((a, b) => a.level - b.level);
    
    container.innerHTML = `
        <div class="timeline">
            ${sortedMissions.map((mission, index) => {
                const isCompleted = mission.completed;
                const isActive = !isCompleted && index > 0 && sortedMissions[index - 1].completed;
                
                return `
                    <div class="timeline-item ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''} animate-fade-in-up stagger-${Math.min(index + 1, 10)}">
                        <div class="timeline-content">
                            <div class="timeline-level">LV.${mission.level}</div>
                            <div class="timeline-name">${escapeHtml(mission.name)}</div>
                            <div class="timeline-district">${escapeHtml(mission.district)}</div>
                        </div>
                        ${index < sortedMissions.length - 1 ? '<div class="timeline-arrow">DOWN_ARROW</div>' : ''}
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

/**
 * Render statistics
 */
function renderStatistics(container) {
    if (!container) return;
    
    const completed = missions.filter(m => m.completed).length;
    const remaining = missions.length - completed;
    const completionPercent = missions.length > 0 ? Math.round((completed / missions.length) * 100) : 0;
    const avgLevel = missions.length > 0 ? Math.round(missions.reduce((sum, m) => sum + m.level, 0) / missions.length) : 0;
    const avgDifficulty = missions.length > 0 ? (missions.reduce((sum, m) => sum + m.difficulty, 0) / missions.length).toFixed(1) : '0.0';
    const priorityMission = missions.filter(m => !m.completed).sort((a, b) => b.priority - a.priority)[0];
    
    container.innerHTML = `
        <div class="stat-grid" style="margin-bottom: var(--spacing-xl);">
            <div class="stat-item animate-fade-in-up stagger-1">
                <span class="stat-value">${completed}</span>
                <span class="stat-label">Completed</span>
            </div>
            <div class="stat-item animate-fade-in-up stagger-2">
                <span class="stat-value">${remaining}</span>
                <span class="stat-label">Remaining</span>
            </div>
            <div class="stat-item animate-fade-in-up stagger-3">
                <span class="stat-value">${completionPercent}%</span>
                <span class="stat-label">Completion</span>
            </div>
            <div class="stat-item animate-fade-in-up stagger-4">
                <span class="stat-value">${avgLevel}</span>
                <span class="stat-label">Avg Level</span>
            </div>
            <div class="stat-item animate-fade-in-up stagger-5">
                <span class="stat-value">${avgDifficulty}</span>
                <span class="stat-label">Avg Difficulty</span>
            </div>
            <div class="stat-item animate-fade-in-up stagger-6" style="grid-column: span 2;">
                <span class="stat-value" style="font-size: 1rem;">${priorityMission ? escapeHtml(priorityMission.name) : 'NONE'}</span>
                <span class="stat-label">Priority Mission</span>
            </div>
        </div>
        
        <div class="card animate-fade-in-up stagger-7">
            <div class="card-header">
                <div class="card-title">PROGRESS OVERVIEW</div>
            </div>
            <div class="card-body">
                <div class="progress-label">
                    <span>Overall Completion</span>
                    <span class="progress-value">${completionPercent}%</span>
                </div>
                <div class="progress-container" style="margin-bottom: var(--spacing-lg);">
                    <div class="progress-bar" style="width: ${completionPercent}%"></div>
                </div>
                <div class="progress-label">
                    <span>Missions Completed</span>
                    <span class="progress-value">${completed} / ${missions.length}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: ${completionPercent}%"></div>
                </div>
            </div>
        </div>
    `;
}

export {
    loadMissions,
    getMissions,
    getMissionById,
    createMission,
    updateMission,
    deleteMission,
    toggleMissionComplete,
    filterMissions,
    sortMissions,
    getDistricts,
    renderMissionCards,
    renderFilterBar,
    renderRecommendedMission,
    renderTimeline,
    renderStatistics,
    refreshMissionsView,
    openMissionModal,
    renderDifficultyStars
};
