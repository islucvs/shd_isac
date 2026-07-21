/**
 * Modal Module
 * Extended modal functionality for mission management
 */

import { modal, toast } from './ui.js';
import { createMission, updateMission, deleteMission, getMissionById } from './missions.js';
import { refreshMissionsView } from './missions.js';

/**
 * Open Create Mission Modal
 */
function openCreateMissionModal() {
    const content = document.createElement('div');
    content.innerHTML = `
        <h3 style="font-family: var(--font-display); font-size: 1.1rem; color: var(--color-accent-primary); margin-bottom: var(--spacing-lg); text-transform: uppercase; letter-spacing: 2px;">
            NEW MISSION
        </h3>
        <form id="create-mission-form">
            <div class="form-group">
                <label class="form-label">Mission Name *</label>
                <input type="text" class="form-input" id="modal-mission-name" placeholder="Enter mission name" required>
            </div>
            <div class="form-group">
                <label class="form-label">District *</label>
                <input type="text" class="form-input" id="modal-mission-district" placeholder="Enter district" required>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md);">
                <div class="form-group">
                    <label class="form-label">Required Level *</label>
                    <input type="number" class="form-input" id="modal-mission-level" value="1" min="1" max="30" required>
                </div>
                <div class="form-group">
                    <label class="form-label">XP Reward *</label>
                    <input type="number" class="form-input" id="modal-mission-xp" value="0" min="0" required>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md);">
                <div class="form-group">
                    <label class="form-label">Difficulty (1-5) *</label>
                    <input type="number" class="form-input" id="modal-mission-difficulty" value="1" min="1" max="5" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Priority (1-5) *</label>
                    <input type="number" class="form-input" id="modal-mission-priority" value="1" min="1" max="5" required>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Notes</label>
                <textarea class="form-textarea" id="modal-mission-notes" rows="3" placeholder="Optional mission notes..."></textarea>
            </div>
            <div class="btn-group" style="justify-content: flex-end; margin-top: var(--spacing-lg);">
                <button type="button" class="btn" id="modal-cancel">CANCEL</button>
                <button type="submit" class="btn btn-primary">CREATE MISSION</button>
            </div>
        </form>
    `;
    
    const modalEl = modal.open(content, { maxWidth: '500px' });
    
    modalEl.querySelector('#modal-cancel').addEventListener('click', () => {
        modal.close();
    });
    
    modalEl.querySelector('#create-mission-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const missionData = {
            name: document.getElementById('modal-mission-name').value.trim(),
            district: document.getElementById('modal-mission-district').value.trim(),
            level: parseInt(document.getElementById('modal-mission-level').value),
            xp: parseInt(document.getElementById('modal-mission-xp').value),
            difficulty: parseInt(document.getElementById('modal-mission-difficulty').value),
            priority: parseInt(document.getElementById('modal-mission-priority').value),
            notes: document.getElementById('modal-mission-notes').value.trim()
        };
        
        const result = await createMission(missionData);
        if (result) {
            modal.close();
            refreshMissionsView();
        }
    });
}

/**
 * Open Edit Mission Modal
 */
function openEditMissionModal(missionId) {
    const mission = getMissionById(missionId);
    if (!mission) {
        toast.error('Mission not found', 'ERROR');
        return;
    }
    
    const content = document.createElement('div');
    content.innerHTML = `
        <h3 style="font-family: var(--font-display); font-size: 1.1rem; color: var(--color-accent-primary); margin-bottom: var(--spacing-lg); text-transform: uppercase; letter-spacing: 2px;">
            EDIT MISSION
        </h3>
        <form id="edit-mission-form">
            <div class="form-group">
                <label class="form-label">Mission Name *</label>
                <input type="text" class="form-input" id="edit-mission-name" value="${mission.name}" required>
            </div>
            <div class="form-group">
                <label class="form-label">District *</label>
                <input type="text" class="form-input" id="edit-mission-district" value="${mission.district}" required>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md);">
                <div class="form-group">
                    <label class="form-label">Required Level *</label>
                    <input type="number" class="form-input" id="edit-mission-level" value="${mission.level}" min="1" max="30" required>
                </div>
                <div class="form-group">
                    <label class="form-label">XP Reward *</label>
                    <input type="number" class="form-input" id="edit-mission-xp" value="${mission.xp}" min="0" required>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md);">
                <div class="form-group">
                    <label class="form-label">Difficulty (1-5) *</label>
                    <input type="number" class="form-input" id="edit-mission-difficulty" value="${mission.difficulty}" min="1" max="5" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Priority (1-5) *</label>
                    <input type="number" class="form-input" id="edit-mission-priority" value="${mission.priority}" min="1" max="5" required>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Status</label>
                <div class="checkbox-container">
                    <input type="checkbox" id="edit-mission-completed" ${mission.completed ? 'checked' : ''}>
                    <span class="checkbox-label">Mission Completed</span>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Notes</label>
                <textarea class="form-textarea" id="edit-mission-notes" rows="3">${mission.notes || ''}</textarea>
            </div>
            <div class="btn-group" style="justify-content: flex-end; margin-top: var(--spacing-lg);">
                <button type="button" class="btn" id="modal-cancel">CANCEL</button>
                <button type="submit" class="btn btn-primary">UPDATE MISSION</button>
            </div>
        </form>
    `;
    
    const modalEl = modal.open(content, { maxWidth: '500px' });
    
    modalEl.querySelector('#modal-cancel').addEventListener('click', () => {
        modal.close();
    });
    
    modalEl.querySelector('#edit-mission-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const missionData = {
            name: document.getElementById('edit-mission-name').value.trim(),
            district: document.getElementById('edit-mission-district').value.trim(),
            level: parseInt(document.getElementById('edit-mission-level').value),
            xp: parseInt(document.getElementById('edit-mission-xp').value),
            difficulty: parseInt(document.getElementById('edit-mission-difficulty').value),
            priority: parseInt(document.getElementById('edit-mission-priority').value),
            completed: document.getElementById('edit-mission-completed').checked,
            notes: document.getElementById('edit-mission-notes').value.trim()
        };
        
        const result = await updateMission(missionId, missionData);
        if (result) {
            modal.close();
            refreshMissionsView();
        }
    });
}

/**
 * Open Delete Confirmation Modal
 */
async function openDeleteModal(missionId) {
    const mission = getMissionById(missionId);
    if (!mission) {
        toast.error('Mission not found', 'ERROR');
        return false;
    }
    
    const confirmed = await modal.confirm(
        `Are you sure you want to permanently delete mission "${mission.name}"? This action cannot be undone.`,
        'CONFIRM DELETION'
    );
    
    if (confirmed) {
        const success = await deleteMission(missionId);
        if (success) {
            refreshMissionsView();
        }
        return success;
    }
    
    return false;
}

/**
 * Open Mission Details Modal
 */
function openMissionDetailsModal(missionId) {
    const mission = getMissionById(missionId);
    if (!mission) return;
    
    const content = document.createElement('div');
    content.innerHTML = `
        <h3 style="font-family: var(--font-display); font-size: 1.1rem; color: var(--color-accent-primary); margin-bottom: var(--spacing-lg); text-transform: uppercase; letter-spacing: 2px;">
            MISSION DETAILS
        </h3>
        <div style="margin-bottom: var(--spacing-lg);">
            <div style="font-family: var(--font-display); font-size: 1.3rem; margin-bottom: var(--spacing-sm); color: var(--color-text-primary);">
                ${mission.name}
            </div>
            <div style="color: var(--color-text-secondary); margin-bottom: var(--spacing-md);">
                ${mission.district}
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--spacing-md); margin-bottom: var(--spacing-md);">
                <div style="background: rgba(255, 106, 0, 0.05); padding: var(--spacing-md); border: 1px solid var(--color-glass-border); border-radius: var(--border-radius-md);">
                    <div style="font-size: 0.75rem; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 1px;">Level</div>
                    <div style="font-family: var(--font-display); font-size: 1.2rem; color: var(--color-accent-primary);">${mission.level}</div>
                </div>
                <div style="background: rgba(255, 106, 0, 0.05); padding: var(--spacing-md); border: 1px solid var(--color-glass-border); border-radius: var(--border-radius-md);">
                    <div style="font-size: 0.75rem; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 1px;">XP</div>
                    <div style="font-family: var(--font-display); font-size: 1.2rem; color: var(--color-accent-primary);">${mission.xp.toLocaleString()}</div>
                </div>
                <div style="background: rgba(255, 106, 0, 0.05); padding: var(--spacing-md); border: 1px solid var(--color-glass-border); border-radius: var(--border-radius-md);">
                    <div style="font-size: 0.75rem; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 1px;">Difficulty</div>
                    <div style="font-family: var(--font-display); font-size: 1.2rem; color: var(--color-accent-primary);">${mission.difficulty}/5</div>
                </div>
                <div style="background: rgba(255, 106, 0, 0.05); padding: var(--spacing-md); border: 1px solid var(--color-glass-border); border-radius: var(--border-radius-md);">
                    <div style="font-size: 0.75rem; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 1px;">Priority</div>
                    <div style="font-family: var(--font-display); font-size: 1.2rem; color: var(--color-accent-primary);">${mission.priority}/5</div>
                </div>
            </div>
            ${mission.notes ? `
                <div style="background: var(--color-bg-tertiary); padding: var(--spacing-md); border-radius: var(--border-radius-md); margin-bottom: var(--spacing-md);">
                    <div style="font-size: 0.75rem; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 1px; margin-bottom: var(--spacing-xs);">Notes</div>
                    <div style="color: var(--color-text-primary); font-style: italic;">${mission.notes}</div>
                </div>
            ` : ''}
            <div style="display: flex; align-items: center; gap: var(--spacing-sm);">
                <span style="font-size: 0.8rem; color: var(--color-text-secondary);">Status:</span>
                <span class="badge ${mission.completed ? 'badge-success' : 'badge-pending'}">${mission.completed ? 'COMPLETED' : 'PENDING'}</span>
            </div>
        </div>
        <div class="btn-group" style="justify-content: flex-end;">
            <button class="btn" id="modal-close">CLOSE</button>
            <button class="btn btn-primary" id="modal-edit">EDIT</button>
        </div>
    `;
    
    const modalEl = modal.open(content, { maxWidth: '450px' });
    
    modalEl.querySelector('#modal-close').addEventListener('click', () => {
        modal.close();
    });
    
    modalEl.querySelector('#modal-edit').addEventListener('click', () => {
        modal.close();
        setTimeout(() => openEditMissionModal(missionId), 350);
    });
}

export {
    openCreateMissionModal,
    openEditMissionModal,
    openDeleteModal,
    openMissionDetailsModal
};
