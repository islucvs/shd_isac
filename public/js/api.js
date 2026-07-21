/**
 * API Module
 * Handles all HTTP requests to the backend
 */

const API_BASE = '';

/**
 * Generic fetch wrapper with error handling
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    const config = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return await response.text();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
}

/**
 * Player API
 */
export const PlayerAPI = {
    /**
     * Get player data
     */
    async get() {
        return apiRequest('/api/player');
    },
    
    /**
     * Update player data
     */
    async update(playerData) {
        return apiRequest('/api/player', {
            method: 'PUT',
            body: JSON.stringify(playerData)
        });
    }
};

/**
 * Missions API
 */
export const MissionsAPI = {
    /**
     * Get all missions
     */
    async getAll() {
        return apiRequest('/api/missions');
    },
    
    /**
     * Get mission by ID
     */
    async getById(id) {
        return apiRequest(`/api/missions/${id}`);
    },
    
    /**
     * Create new mission
     */
    async create(missionData) {
        return apiRequest('/api/missions', {
            method: 'POST',
            body: JSON.stringify(missionData)
        });
    },
    
    /**
     * Update mission
     */
    async update(id, missionData) {
        return apiRequest(`/api/missions/${id}`, {
            method: 'PUT',
            body: JSON.stringify(missionData)
        });
    },
    
    /**
     * Delete mission
     */
    async delete(id) {
        return apiRequest(`/api/missions/${id}`, {
            method: 'DELETE'
        });
    }
};

export { apiRequest };
