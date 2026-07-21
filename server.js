const express = require('express');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Data file paths
const MISSIONS_FILE = path.join(__dirname, 'data', 'missions.json');
const PLAYER_FILE = path.join(__dirname, 'data', 'player.json');

// Helper: Read JSON file
async function readJsonFile(filePath, defaultValue) {
    try {
        const data = await fs.readFile(filePath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        if (error.code === 'ENOENT') {
            await fs.writeFile(filePath, JSON.stringify(defaultValue, null, 2));
            return defaultValue;
        }
        throw error;
    }
}

// Helper: Write JSON file
async function writeJsonFile(filePath, data) {
    await fs.writeFile(filePath, JSON.stringify(data, null, 2));
}

// ==================== PLAYER API ====================

// GET /api/player - Get player data
app.get('/api/player', async (req, res) => {
    try {
        const player = await readJsonFile(PLAYER_FILE, {
            "name": "Agent",
            "level": 9,
            "firepower": 4000,
            "toughness": 5000,
            "skillPower": 4000,
            "district": "Hudson Yards",
            "xp": 3400
        });
        res.json(player);
    } catch (error) {
        res.status(500).json({ error: 'Failed to read player data' });
    }
});

// PUT /api/player - Update player data
app.put('/api/player', async (req, res) => {
    try {
        const currentPlayer = await readJsonFile(PLAYER_FILE, {
            "name": "Agent",
            "level": 9,
            "firepower": 4000,
            "toughness": 5000,
            "skillPower": 4000,
            "district": "Hudson Yards",
            "xp": 3400
        });
        const updatedPlayer = { ...currentPlayer, ...req.body };
        await writeJsonFile(PLAYER_FILE, updatedPlayer);
        res.json(updatedPlayer);
    } catch (error) {
        res.status(500).json({ error: 'Failed to update player data' });
    }
});

// ==================== MISSIONS API ====================

// GET /api/missions - Get all missions
app.get('/api/missions', async (req, res) => {
    try {
        const missions = await readJsonFile(MISSIONS_FILE, []);
        res.json(missions);
    } catch (error) {
        res.status(500).json({ error: 'Failed to read missions data' });
    }
});

// GET /api/missions/:id - Get mission by ID
app.get('/api/missions/:id', async (req, res) => {
    try {
        const missions = await readJsonFile(MISSIONS_FILE, []);
        const mission = missions.find(m => m.id === parseInt(req.params.id));
        if (!mission) {
            return res.status(404).json({ error: 'Mission not found' });
        }
        res.json(mission);
    } catch (error) {
        res.status(500).json({ error: 'Failed to read mission data' });
    }
});

// POST /api/missions - Create new mission
app.post('/api/missions', async (req, res) => {
    try {
        const missions = await readJsonFile(MISSIONS_FILE, []);
        const newMission = {
            id: missions.length > 0 ? Math.max(...missions.map(m => m.id)) + 1 : 1,
            name: req.body.name || '',
            district: req.body.district || '',
            level: req.body.level || 1,
            difficulty: req.body.difficulty || 1,
            priority: req.body.priority || 1,
            xp: req.body.xp || 0,
            completed: req.body.completed || false,
            notes: req.body.notes || ''
        };
        missions.push(newMission);
        await writeJsonFile(MISSIONS_FILE, missions);
        res.status(201).json(newMission);
    } catch (error) {
        res.status(500).json({ error: 'Failed to create mission' });
    }
});

// PUT /api/missions/:id - Update mission
app.put('/api/missions/:id', async (req, res) => {
    try {
        const missions = await readJsonFile(MISSIONS_FILE, []);
        const index = missions.findIndex(m => m.id === parseInt(req.params.id));
        if (index === -1) {
            return res.status(404).json({ error: 'Mission not found' });
        }
        missions[index] = { ...missions[index], ...req.body };
        await writeJsonFile(MISSIONS_FILE, missions);
        res.json(missions[index]);
    } catch (error) {
        res.status(500).json({ error: 'Failed to update mission' });
    }
});

// DELETE /api/missions/:id - Delete mission
app.delete('/api/missions/:id', async (req, res) => {
    try {
        const missions = await readJsonFile(MISSIONS_FILE, []);
        const index = missions.findIndex(m => m.id === parseInt(req.params.id));
        if (index === -1) {
            return res.status(404).json({ error: 'Mission not found' });
        }
        const deletedMission = missions.splice(index, 1)[0];
        await writeJsonFile(MISSIONS_FILE, missions);
        res.json(deletedMission);
    } catch (error) {
        res.status(500).json({ error: 'Failed to delete mission' });
    }
});

// Global error handler
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
    console.log(`Division Agent Progress Tracker running on port ${PORT}`);
    console.log(`Open http://localhost:${PORT} in your browser`);
});

module.exports = app;
