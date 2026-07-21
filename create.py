import os

# Create the folder structure
base_dir = "C:/Users/lucas/Downloads/shd"
folders = [
    f"{base_dir}/data",
    f"{base_dir}/public/css",
    f"{base_dir}/public/js",
    f"{base_dir}/public/assets"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

print("Folder structure created successfully!")

# 1. package.json
package_json = '''{
  "name": "division-agent-progress-tracker",
  "version": "1.0.0",
  "description": "A Division 1 inspired agent progress tracker with military HUD UI",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "node server.js"
  },
  "keywords": [
    "division",
    "tracker",
    "hud",
    "military",
    "progress"
  ],
  "author": "Senior Full Stack Engineer",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2"
  }
}'''

with open(f"{base_dir}/package.json", "w") as f:
    f.write(package_json)

print("package.json created!")

# 2. server.js
server_js = '''const express = require('express');
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

// Serve index.html for all other routes (SPA support)
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
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
'''

with open(f"{base_dir}/server.js", "w") as f:
    f.write(server_js)

print("server.js created!")

# 3. data/missions.json
missions_json = '''[
  {
    "id": 1,
    "name": "Madison Field Hospital",
    "district": "Hudson Yards",
    "level": 8,
    "difficulty": 2,
    "priority": 5,
    "xp": 2200,
    "completed": false,
    "notes": "Rescue Dr. Kandel from the hospital."
  },
  {
    "id": 2,
    "name": "Lincoln Tunnel Checkpoint",
    "district": "Hudson Yards",
    "level": 10,
    "difficulty": 3,
    "priority": 5,
    "xp": 2800,
    "completed": false,
    "notes": "Clear the tunnel and secure the checkpoint."
  },
  {
    "id": 3,
    "name": "Amherst's Apartment",
    "district": "Hudson Yards",
    "level": 12,
    "difficulty": 3,
    "priority": 4,
    "xp": 3200,
    "completed": false,
    "notes": "Investigate the outbreak origin."
  },
  {
    "id": 4,
    "name": "Times Square Power Relay",
    "district": "Times Square",
    "level": 14,
    "difficulty": 4,
    "priority": 4,
    "xp": 3800,
    "completed": false,
    "notes": "Restore power to the grid."
  },
  {
    "id": 5,
    "name": "Broadway Emporium",
    "district": "Times Square",
    "level": 16,
    "difficulty": 4,
    "priority": 3,
    "xp": 4200,
    "completed": false,
    "notes": "Secure the supplies."
  },
  {
    "id": 6,
    "name": "Napalm Production Site",
    "district": "Chelsea",
    "level": 18,
    "difficulty": 5,
    "priority": 5,
    "xp": 4800,
    "completed": false,
    "notes": "Destroy the napalm production facility."
  },
  {
    "id": 7,
    "name": "Police Academy",
    "district": "Chelsea",
    "level": 20,
    "difficulty": 5,
    "priority": 4,
    "xp": 5200,
    "completed": false,
    "notes": "Secure the academy and rescue cadets."
  },
  {
    "id": 8,
    "name": "Grand Central Station",
    "district": "Midtown East",
    "level": 22,
    "difficulty": 5,
    "priority": 5,
    "xp": 5800,
    "completed": false,
    "notes": "Retake Grand Central from the LMB."
  },
  {
    "id": 9,
    "name": "Lexington Event Center",
    "district": "Midtown East",
    "level": 24,
    "difficulty": 5,
    "priority": 4,
    "xp": 6200,
    "completed": false,
    "notes": "Clear the Rikers from the event center."
  },
  {
    "id": 10,
    "name": "Rooftop Comm Relay",
    "district": "Murray Hill",
    "level": 26,
    "difficulty": 4,
    "priority": 3,
    "xp": 6800,
    "completed": false,
    "notes": "Restore the communications relay."
  },
  {
    "id": 11,
    "name": "Queens Tunnel Camp",
    "district": "Murray Hill",
    "level": 28,
    "difficulty": 5,
    "priority": 4,
    "xp": 7200,
    "completed": false,
    "notes": "Clear the tunnel camp."
  },
  {
    "id": 12,
    "name": "United Nations Assembly",
    "district": "Midtown East",
    "level": 30,
    "difficulty": 5,
    "priority": 5,
    "xp": 8500,
    "completed": false,
    "notes": "Final mission. Stop the LMB leader."
  }
]'''

with open(f"{base_dir}/data/missions.json", "w") as f:
    f.write(missions_json)

# 4. data/player.json
player_json = '''{
  "name": "Agent",
  "level": 9,
  "firepower": 4000,
  "toughness": 5000,
  "skillPower": 4000,
  "district": "Hudson Yards",
  "xp": 3400
}'''

with open(f"{base_dir}/data/player.json", "w") as f:
    f.write(player_json)

print("Data files created!")

# 5. public/css/style.css
style_css = '''/* ============================================
   DIVISION AGENT PROGRESS TRACKER
   Main Stylesheet - Military HUD Theme
   ============================================ */

/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

/* CSS Variables */
:root {
    --color-bg-primary: #111111;
    --color-bg-secondary: #181818;
    --color-bg-tertiary: #252525;
    --color-accent-primary: #ff6a00;
    --color-accent-secondary: #ff8d1a;
    --color-text-primary: #ffffff;
    --color-text-secondary: #808080;
    --color-border: rgba(255, 106, 0, 0.3);
    --color-glass: rgba(24, 24, 24, 0.85);
    --color-glass-border: rgba(255, 106, 0, 0.15);
    
    --font-display: 'Orbitron', sans-serif;
    --font-body: 'Rajdhani', sans-serif;
    
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    
    --border-radius-sm: 2px;
    --border-radius-md: 4px;
    --border-radius-lg: 8px;
    
    --transition-fast: 0.15s ease;
    --transition-normal: 0.3s ease;
    --transition-slow: 0.5s ease;
    
    --sidebar-width: 240px;
    --topbar-height: 60px;
    --right-panel-width: 280px;
}

/* Reset & Base */
*, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    font-size: 16px;
    scroll-behavior: smooth;
}

body {
    font-family: var(--font-body);
    background-color: var(--color-bg-primary);
    color: var(--color-text-primary);
    min-height: 100vh;
    overflow-x: hidden;
    line-height: 1.5;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: var(--color-bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--color-accent-primary);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--color-accent-secondary);
}

/* Selection */
::selection {
    background: var(--color-accent-primary);
    color: var(--color-bg-primary);
}

/* ============================================
   LAYOUT
   ============================================ */

.app-container {
    display: grid;
    grid-template-areas:
        "sidebar topbar topbar"
        "sidebar main right-panel";
    grid-template-columns: var(--sidebar-width) 1fr var(--right-panel-width);
    grid-template-rows: var(--topbar-height) 1fr;
    min-height: 100vh;
    position: relative;
}

/* Background Grid Effect */
.app-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        linear-gradient(rgba(255, 106, 0, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 106, 0, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none;
    z-index: 0;
}

/* Scanlines */
.app-container::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 0, 0, 0.1) 2px,
        rgba(0, 0, 0, 0.1) 4px
    );
    pointer-events: none;
    z-index: 1;
}

/* ============================================
   SIDEBAR
   ============================================ */

.sidebar {
    grid-area: sidebar;
    background: var(--color-glass);
    border-right: 1px solid var(--color-glass-border);
    backdrop-filter: blur(10px);
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 10;
    padding: var(--spacing-lg) 0;
}

.sidebar-logo {
    padding: 0 var(--spacing-lg) var(--spacing-lg);
    border-bottom: 1px solid var(--color-glass-border);
    margin-bottom: var(--spacing-lg);
}

.sidebar-logo h1 {
    font-family: var(--font-display);
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--color-accent-primary);
    text-transform: uppercase;
    letter-spacing: 2px;
    line-height: 1.3;
}

.sidebar-logo span {
    display: block;
    font-size: 0.7rem;
    color: var(--color-text-secondary);
    letter-spacing: 4px;
    margin-top: var(--spacing-xs);
}

.sidebar-nav {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    padding: 0 var(--spacing-md);
}

.nav-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    border-radius: var(--border-radius-md);
    cursor: pointer;
    transition: all var(--transition-fast);
    border: 1px solid transparent;
    text-decoration: none;
    color: var(--color-text-secondary);
    font-family: var(--font-body);
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.nav-item:hover {
    background: rgba(255, 106, 0, 0.1);
    border-color: var(--color-border);
    color: var(--color-accent-secondary);
}

.nav-item.active {
    background: rgba(255, 106, 0, 0.15);
    border-color: var(--color-accent-primary);
    color: var(--color-accent-primary);
    box-shadow: 0 0 15px rgba(255, 106, 0, 0.2);
}

.nav-item i {
    font-size: 1.1rem;
    width: 24px;
    text-align: center;
}

.nav-item .nav-label {
    flex: 1;
}

.nav-item .nav-badge {
    background: var(--color-accent-primary);
    color: var(--color-bg-primary);
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 700;
}

.sidebar-footer {
    padding: var(--spacing-md) var(--spacing-lg);
    border-top: 1px solid var(--color-glass-border);
    margin-top: auto;
}

.sidebar-footer .version {
    font-size: 0.75rem;
    color: var(--color-text-secondary);
    text-align: center;
    letter-spacing: 2px;
}

/* ============================================
   TOP BAR
   ============================================ */

.topbar {
    grid-area: topbar;
    background: var(--color-glass);
    border-bottom: 1px solid var(--color-glass-border);
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--spacing-lg);
    position: relative;
    z-index: 10;
}

.topbar-left {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
}

.agent-info {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.agent-info .agent-name {
    font-family: var(--font-display);
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    letter-spacing: 1px;
}

.agent-info .agent-level {
    background: var(--color-accent-primary);
    color: var(--color-bg-primary);
    padding: 2px 10px;
    border-radius: var(--border-radius-sm);
    font-size: 0.8rem;
    font-weight: 700;
}

.agent-info .agent-district {
    color: var(--color-text-secondary);
    font-size: 0.85rem;
    border-left: 1px solid var(--color-glass-border);
    padding-left: var(--spacing-md);
}

.topbar-center {
    flex: 1;
    max-width: 400px;
    margin: 0 var(--spacing-lg);
}

.search-bar {
    position: relative;
    width: 100%;
}

.search-bar input {
    width: 100%;
    background: var(--color-bg-tertiary);
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-sm) var(--spacing-md) var(--spacing-sm) 40px;
    color: var(--color-text-primary);
    font-family: var(--font-body);
    font-size: 0.9rem;
    outline: none;
    transition: all var(--transition-fast);
}

.search-bar input:focus {
    border-color: var(--color-accent-primary);
    box-shadow: 0 0 10px rgba(255, 106, 0, 0.2);
}

.search-bar input::placeholder {
    color: var(--color-text-secondary);
}

.search-bar .search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--color-text-secondary);
    font-size: 0.9rem;
}

.topbar-right {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
}

.current-time {
    font-family: var(--font-display);
    font-size: 0.9rem;
    color: var(--color-accent-primary);
    letter-spacing: 2px;
}

/* ============================================
   MAIN CONTENT
   ============================================ */

.main-content {
    grid-area: main;
    padding: var(--spacing-lg);
    overflow-y: auto;
    position: relative;
    z-index: 5;
}

.page-title {
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-text-primary);
    margin-bottom: var(--spacing-lg);
    text-transform: uppercase;
    letter-spacing: 3px;
    position: relative;
    padding-bottom: var(--spacing-md);
}

.page-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 60px;
    height: 2px;
    background: var(--color-accent-primary);
    box-shadow: 0 0 10px var(--color-accent-primary);
}

/* ============================================
   RIGHT PANEL
   ============================================ */

.right-panel {
    grid-area: right-panel;
    background: var(--color-glass);
    border-left: 1px solid var(--color-glass-border);
    backdrop-filter: blur(10px);
    padding: var(--spacing-lg);
    overflow-y: auto;
    position: relative;
    z-index: 10;
}

.panel-section {
    margin-bottom: var(--spacing-xl);
}

.panel-section-title {
    font-family: var(--font-display);
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--color-accent-primary);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: var(--spacing-md);
    padding-bottom: var(--spacing-sm);
    border-bottom: 1px solid var(--color-glass-border);
}

/* ============================================
   CARDS
   ============================================ */

.card {
    background: var(--color-glass);
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
    transition: all var(--transition-normal);
    position: relative;
    overflow: hidden;
}

.card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--color-accent-primary), transparent);
    opacity: 0;
    transition: opacity var(--transition-normal);
}

.card:hover {
    border-color: var(--color-border);
    box-shadow: 0 0 20px rgba(255, 106, 0, 0.1);
    transform: translateY(-2px);
}

.card:hover::before {
    opacity: 1;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--spacing-md);
}

.card-title {
    font-family: var(--font-display);
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    letter-spacing: 1px;
}

.card-subtitle {
    font-size: 0.85rem;
    color: var(--color-text-secondary);
    margin-top: var(--spacing-xs);
}

.card-body {
    color: var(--color-text-secondary);
    font-size: 0.9rem;
}

/* ============================================
   BUTTONS
   ============================================ */

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-sm);
    background: var(--color-bg-tertiary);
    color: var(--color-text-primary);
    font-family: var(--font-body);
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all var(--transition-fast);
    outline: none;
    text-decoration: none;
}

.btn:hover {
    border-color: var(--color-accent-primary);
    color: var(--color-accent-primary);
    box-shadow: 0 0 10px rgba(255, 106, 0, 0.2);
}

.btn:active {
    transform: scale(0.98);
}

.btn-primary {
    background: var(--color-accent-primary);
    border-color: var(--color-accent-primary);
    color: var(--color-bg-primary);
}

.btn-primary:hover {
    background: var(--color-accent-secondary);
    border-color: var(--color-accent-secondary);
    color: var(--color-bg-primary);
    box-shadow: 0 0 15px rgba(255, 106, 0, 0.4);
}

.btn-danger {
    border-color: #cc3333;
    color: #ff6666;
}

.btn-danger:hover {
    background: rgba(204, 51, 51, 0.2);
    border-color: #ff6666;
    box-shadow: 0 0 10px rgba(255, 102, 102, 0.3);
}

.btn-success {
    border-color: #33cc33;
    color: #66ff66;
}

.btn-success:hover {
    background: rgba(51, 204, 51, 0.2);
    border-color: #66ff66;
    box-shadow: 0 0 10px rgba(102, 255, 102, 0.3);
}

.btn-sm {
    padding: 4px 10px;
    font-size: 0.75rem;
}

.btn-group {
    display: flex;
    gap: var(--spacing-sm);
    flex-wrap: wrap;
}

/* ============================================
   FORMS
   ============================================ */

.form-group {
    margin-bottom: var(--spacing-md);
}

.form-label {
    display: block;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-xs);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.form-input,
.form-select,
.form-textarea {
    width: 100%;
    background: var(--color-bg-tertiary);
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    color: var(--color-text-primary);
    font-family: var(--font-body);
    font-size: 0.9rem;
    outline: none;
    transition: all var(--transition-fast);
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
    border-color: var(--color-accent-primary);
    box-shadow: 0 0 10px rgba(255, 106, 0, 0.2);
}

.form-input::placeholder,
.form-textarea::placeholder {
    color: var(--color-text-secondary);
}

.form-textarea {
    resize: vertical;
    min-height: 80px;
}

/* ============================================
   PROGRESS BARS
   ============================================ */

.progress-container {
    width: 100%;
    height: 8px;
    background: var(--color-bg-tertiary);
    border-radius: 4px;
    overflow: hidden;
    position: relative;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--color-accent-primary), var(--color-accent-secondary));
    border-radius: 4px;
    transition: width 1s ease;
    position: relative;
}

.progress-bar::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 20px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3));
    animation: progress-shine 2s infinite;
}

.progress-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--spacing-xs);
    font-size: 0.8rem;
}

.progress-label span {
    color: var(--color-text-secondary);
}

.progress-label .progress-value {
    color: var(--color-accent-primary);
    font-weight: 600;
}

/* ============================================
   STATS & METRICS
   ============================================ */

.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: var(--spacing-md);
}

.stat-item {
    text-align: center;
    padding: var(--spacing-md);
    background: rgba(255, 106, 0, 0.05);
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-md);
    transition: all var(--transition-fast);
}

.stat-item:hover {
    border-color: var(--color-border);
    background: rgba(255, 106, 0, 0.1);
}

.stat-value {
    font-family: var(--font-display);
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--color-accent-primary);
    display: block;
}

.stat-label {
    font-size: 0.75rem;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: var(--spacing-xs);
}

/* ============================================
   DIFFICULTY STARS
   ============================================ */

.difficulty-stars {
    display: flex;
    gap: 2px;
}

.difficulty-star {
    color: var(--color-text-secondary);
    font-size: 0.9rem;
}

.difficulty-star.active {
    color: var(--color-accent-primary);
    text-shadow: 0 0 5px rgba(255, 106, 0, 0.5);
}

/* ============================================
   CHECKBOX
   ============================================ */

.checkbox-container {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    cursor: pointer;
}

.checkbox-container input[type="checkbox"] {
    appearance: none;
    width: 18px;
    height: 18px;
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-sm);
    background: var(--color-bg-tertiary);
    cursor: pointer;
    position: relative;
    transition: all var(--transition-fast);
}

.checkbox-container input[type="checkbox"]:checked {
    background: var(--color-accent-primary);
    border-color: var(--color-accent-primary);
}

.checkbox-container input[type="checkbox"]:checked::after {
    content: 'V';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: var(--color-bg-primary);
    font-size: 0.7rem;
    font-weight: 700;
}

.checkbox-label {
    font-size: 0.85rem;
    color: var(--color-text-secondary);
}

/* ============================================
   BADGES
   ============================================ */

.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: var(--border-radius-sm);
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.badge-primary {
    background: rgba(255, 106, 0, 0.2);
    color: var(--color-accent-primary);
    border: 1px solid var(--color-border);
}

.badge-success {
    background: rgba(51, 204, 51, 0.2);
    color: #66ff66;
    border: 1px solid rgba(51, 204, 51, 0.3);
}

.badge-pending {
    background: rgba(128, 128, 128, 0.2);
    color: var(--color-text-secondary);
    border: 1px solid rgba(128, 128, 128, 0.3);
}

/* ============================================
   FILTERS & SORT
   ============================================ */

.filter-bar {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
    padding: var(--spacing-md);
    background: var(--color-glass);
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-md);
}

.filter-group {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.filter-group label {
    font-size: 0.8rem;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ============================================
   MISSION CARDS
   ============================================ */

.mission-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--spacing-lg);
}

.mission-card {
    background: var(--color-glass);
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-lg);
    transition: all var(--transition-normal);
    position: relative;
    overflow: hidden;
}

.mission-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: var(--color-accent-primary);
    opacity: 0;
    transition: opacity var(--transition-normal);
}

.mission-card:hover {
    border-color: var(--color-border);
    box-shadow: 0 0 20px rgba(255, 106, 0, 0.1);
    transform: translateY(-2px);
}

.mission-card:hover::before {
    opacity: 1;
}

.mission-card.completed {
    border-color: rgba(255, 106, 0, 0.4);
    background: rgba(255, 106, 0, 0.05);
}

.mission-card.completed::before {
    opacity: 1;
    background: var(--color-accent-primary);
}

.mission-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--spacing-md);
}

.mission-card-title {
    font-family: var(--font-display);
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    letter-spacing: 1px;
}

.mission-card-meta {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
}

.mission-card-meta-item {
    display: flex;
    flex-direction: column;
}

.mission-card-meta-label {
    font-size: 0.7rem;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.mission-card-meta-value {
    font-size: 0.9rem;
    color: var(--color-text-primary);
    font-weight: 600;
}

.mission-card-actions {
    display: flex;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-md);
    padding-top: var(--spacing-md);
    border-top: 1px solid var(--color-glass-border);
}

/* ============================================
   TIMELINE
   ============================================ */

.timeline {
    position: relative;
    padding-left: var(--spacing-xl);
}

.timeline::before {
    content: '';
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--color-glass-border);
}

.timeline-item {
    position: relative;
    padding-bottom: var(--spacing-xl);
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: -22px;
    top: 4px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--color-bg-tertiary);
    border: 2px solid var(--color-text-secondary);
    transition: all var(--transition-normal);
}

.timeline-item.completed::before {
    background: var(--color-accent-primary);
    border-color: var(--color-accent-primary);
    box-shadow: 0 0 10px rgba(255, 106, 0, 0.5);
}

.timeline-item.active::before {
    background: var(--color-accent-primary);
    border-color: var(--color-accent-secondary);
    animation: pulse-orange 2s infinite;
}

.timeline-content {
    background: var(--color-glass);
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-md);
    transition: all var(--transition-normal);
}

.timeline-item.completed .timeline-content {
    border-color: rgba(255, 106, 0, 0.4);
    background: rgba(255, 106, 0, 0.05);
}

.timeline-item.active .timeline-content {
    border-color: var(--color-accent-primary);
    box-shadow: 0 0 15px rgba(255, 106, 0, 0.2);
}

.timeline-level {
    font-family: var(--font-display);
    font-size: 0.8rem;
    color: var(--color-accent-primary);
    margin-bottom: var(--spacing-xs);
}

.timeline-name {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: var(--spacing-xs);
}

.timeline-district {
    font-size: 0.8rem;
    color: var(--color-text-secondary);
}

.timeline-arrow {
    text-align: center;
    color: var(--color-text-secondary);
    font-size: 1.2rem;
    margin: var(--spacing-sm) 0;
}

/* ============================================
   PLAYER CARD
   ============================================ */

.player-card {
    background: var(--color-glass);
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-xl);
    position: relative;
    overflow: hidden;
}

.player-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--color-accent-primary), var(--color-accent-secondary), var(--color-accent-primary));
}

.player-card-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.player-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--color-accent-primary), var(--color-accent-secondary));
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-display);
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-bg-primary);
    border: 3px solid var(--color-accent-primary);
    box-shadow: 0 0 20px rgba(255, 106, 0, 0.3);
}

.player-info h2 {
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-text-primary);
    letter-spacing: 2px;
}

.player-info .player-level {
    font-size: 1rem;
    color: var(--color-accent-primary);
    font-weight: 600;
}

.player-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.player-stat {
    text-align: center;
    padding: var(--spacing-md);
    background: rgba(255, 106, 0, 0.05);
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-md);
}

.player-stat-value {
    font-family: var(--font-display);
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--color-accent-primary);
}

.player-stat-label {
    font-size: 0.8rem;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: var(--spacing-xs);
}

/* ============================================
   SETTINGS
   ============================================ */

.settings-section {
    margin-bottom: var(--spacing-xl);
}

.settings-section-title {
    font-family: var(--font-display);
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: var(--spacing-md);
    text-transform: uppercase;
    letter-spacing: 2px;
}

.setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-md);
    background: var(--color-glass);
    border: 1px solid var(--color-glass-border);
    border-radius: var(--border-radius-md);
    margin-bottom: var(--spacing-md);
}

.setting-item-info h4 {
    font-size: 0.95rem;
    color: var(--color-text-primary);
    margin-bottom: var(--spacing-xs);
}

.setting-item-info p {
    font-size: 0.8rem;
    color: var(--color-text-secondary);
}

/* Toggle Switch */
.toggle-switch {
    position: relative;
    width: 48px;
    height: 24px;
    background: var(--color-bg-tertiary);
    border-radius: 12px;
    cursor: pointer;
    transition: all var(--transition-fast);
    border: 1px solid var(--color-glass-border);
}

.toggle-switch.active {
    background: var(--color-accent-primary);
    border-color: var(--color-accent-primary);
}

.toggle-switch::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--color-text-primary);
    transition: all var(--transition-fast);
}

.toggle-switch.active::after {
    left: 26px;
}

/* ============================================
   TOAST NOTIFICATIONS
   ============================================ */

.toast-container {
    position: fixed;
    bottom: var(--spacing-lg);
    right: var(--spacing-lg);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.toast {
    background: var(--color-glass);
    border: 1px solid var(--color-glass-border);
    border-left: 3px solid var(--color-accent-primary);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-md) var(--spacing-lg);
    min-width: 280px;
    backdrop-filter: blur(10px);
    animation: toast-slide-in 0.3s ease;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.toast.toast-exit {
    animation: toast-slide-out 0.3s ease forwards;
}

.toast-title {
    font-family: var(--font-display);
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin-bottom: var(--spacing-xs);
}

.toast-message {
    font-size: 0.8rem;
    color: var(--color-text-secondary);
}

.toast-success {
    border-left-color: #33cc33;
}

.toast-error {
    border-left-color: #cc3333;
}

.toast-warning {
    border-left-color: #ffcc00;
}

/* ============================================
   LOADING SCREEN
   ============================================ */

.loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--color-bg-primary);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    transition: opacity 0.5s ease, visibility 0.5s ease;
}

.loading-screen.hidden {
    opacity: 0;
    visibility: hidden;
}

.loading-logo {
    font-family: var(--font-display);
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-accent-primary);
    text-transform: uppercase;
    letter-spacing: 4px;
    margin-bottom: var(--spacing-xl);
}

.loading-spinner {
    width: 60px;
    height: 60px;
    border: 3px solid var(--color-glass-border);
    border-top-color: var(--color-accent-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: var(--spacing-lg);
}

.loading-text {
    font-family: var(--font-display);
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    letter-spacing: 2px;
}

.loading-progress {
    width: 200px;
    height: 2px;
    background: var(--color-bg-tertiary);
    margin-top: var(--spacing-lg);
    border-radius: 1px;
    overflow: hidden;
}

.loading-progress-bar {
    height: 100%;
    background: var(--color-accent-primary);
    width: 0%;
    transition: width 0.3s ease;
}

/* ============================================
   EMPTY STATE
   ============================================ */

.empty-state {
    text-align: center;
    padding: var(--spacing-xl) var(--spacing-lg);
    color: var(--color-text-secondary);
}

.empty-state-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-md);
    opacity: 0.5;
}

.empty-state-title {
    font-family: var(--font-display);
    font-size: 1.2rem;
    margin-bottom: var(--spacing-sm);
    color: var(--color-text-primary);
}

.empty-state-text {
    font-size: 0.9rem;
}

/* ============================================
   RESPONSIVE
   ============================================ */

@media (max-width: 1200px) {
    .app-container {
        grid-template-areas:
            "topbar topbar"
            "sidebar main";
        grid-template-columns: var(--sidebar-width) 1fr;
        grid-template-rows: var(--topbar-height) 1fr;
    }
    
    .right-panel {
        display: none;
    }
}

@media (max-width: 768px) {
    :root {
        --sidebar-width: 60px;
    }
    
    .sidebar-logo h1,
    .nav-item .nav-label,
    .nav-item .nav-badge,
    .sidebar-footer {
        display: none;
    }
    
    .nav-item {
        justify-content: center;
        padding: var(--spacing-md) var(--spacing-sm);
    }
    
    .nav-item i {
        width: auto;
    }
    
    .topbar {
        padding: 0 var(--spacing-md);
    }
    
    .topbar-center {
        display: none;
    }
    
    .agent-info .agent-district {
        display: none;
    }
    
    .main-content {
        padding: var(--spacing-md);
    }
    
    .mission-grid {
        grid-template-columns: 1fr;
    }
    
    .player-stats {
        grid-template-columns: 1fr;
    }
    
    .stat-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .filter-bar {
        flex-direction: column;
    }
}

@media (max-width: 480px) {
    .app-container {
        grid-template-areas:
            "topbar"
            "main";
        grid-template-columns: 1fr;
    }
    
    .sidebar {
        display: none;
    }
    
    .mobile-nav {
        display: flex;
    }
}

/* Mobile Navigation (hidden by default) */
.mobile-nav {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--color-glass);
    border-top: 1px solid var(--color-glass-border);
    backdrop-filter: blur(10px);
    z-index: 100;
    justify-content: space-around;
    padding: var(--spacing-sm) 0;
}

.mobile-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: var(--spacing-sm);
    color: var(--color-text-secondary);
    text-decoration: none;
    font-size: 0.7rem;
    transition: color var(--transition-fast);
}

.mobile-nav-item.active {
    color: var(--color-accent-primary);
}

.mobile-nav-item i {
    font-size: 1.2rem;
}
'''

with open(f"{base_dir}/public/css/style.css", "w") as f:
    f.write(style_css)

print("style.css created!")

# 6. public/css/animations.css
animations_css = '''/* ============================================
   DIVISION AGENT PROGRESS TRACKER
   Animations Stylesheet
   ============================================ */

/* ============================================
   KEYFRAMES
   ============================================ */

@keyframes fade-in {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes fade-in-up {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fade-in-down {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fade-in-left {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes fade-in-right {
    from {
        opacity: 0;
        transform: translateX(20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slide-in-left {
    from {
        transform: translateX(-100%);
    }
    to {
        transform: translateX(0);
    }
}

@keyframes slide-in-right {
    from {
        transform: translateX(100%);
    }
    to {
        transform: translateX(0);
    }
}

@keyframes slide-in-up {
    from {
        transform: translateY(100%);
    }
    to {
        transform: translateY(0);
    }
}

@keyframes slide-in-down {
    from {
        transform: translateY(-100%);
    }
    to {
        transform: translateY(0);
    }
}

@keyframes scale-in {
    from {
        opacity: 0;
        transform: scale(0.9);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes scale-out {
    from {
        opacity: 1;
        transform: scale(1);
    }
    to {
        opacity: 0;
        transform: scale(0.9);
    }
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

@keyframes pulse-orange {
    0%, 100% {
        box-shadow: 0 0 5px rgba(255, 106, 0, 0.5);
    }
    50% {
        box-shadow: 0 0 20px rgba(255, 106, 0, 0.8);
    }
}

@keyframes glow {
    0%, 100% {
        box-shadow: 0 0 5px rgba(255, 106, 0, 0.3);
    }
    50% {
        box-shadow: 0 0 20px rgba(255, 106, 0, 0.6);
    }
}

@keyframes glow-text {
    0%, 100% {
        text-shadow: 0 0 5px rgba(255, 106, 0, 0.5);
    }
    50% {
        text-shadow: 0 0 15px rgba(255, 106, 0, 0.8);
    }
}

@keyframes border-glow {
    0%, 100% {
        border-color: rgba(255, 106, 0, 0.3);
    }
    50% {
        border-color: rgba(255, 106, 0, 0.8);
    }
}

@keyframes progress-shine {
    0% {
        transform: translateX(0);
    }
    100% {
        transform: translateX(100px);
    }
}

@keyframes typing {
    from {
        width: 0;
    }
    to {
        width: 100%;
    }
}

@keyframes blink-cursor {
    0%, 100% {
        border-color: transparent;
    }
    50% {
        border-color: var(--color-accent-primary);
    }
}

@keyframes scanline-move {
    0% {
        transform: translateY(-100%);
    }
    100% {
        transform: translateY(100%);
    }
}

@keyframes grid-pulse {
    0%, 100% {
        opacity: 0.03;
    }
    50% {
        opacity: 0.08;
    }
}

@keyframes float {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-10px);
    }
}

@keyframes shake {
    0%, 100% {
        transform: translateX(0);
    }
    10%, 30%, 50%, 70%, 90% {
        transform: translateX(-5px);
    }
    20%, 40%, 60%, 80% {
        transform: translateX(5px);
    }
}

@keyframes toast-slide-in {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes toast-slide-out {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

@keyframes modal-backdrop-in {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes modal-content-in {
    from {
        opacity: 0;
        transform: scale(0.9) translateY(-20px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

@keyframes modal-content-out {
    from {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
    to {
        opacity: 0;
        transform: scale(0.9) translateY(-20px);
    }
}

@keyframes card-hover-glow {
    0%, 100% {
        box-shadow: 0 0 5px rgba(255, 106, 0, 0.1);
    }
    50% {
        box-shadow: 0 0 25px rgba(255, 106, 0, 0.3);
    }
}

@keyframes isac-rotate {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

@keyframes isac-pulse {
    0%, 100% {
        opacity: 0.3;
        transform: scale(0.8);
    }
    50% {
        opacity: 1;
        transform: scale(1.2);
    }
}

@keyframes data-stream {
    0% {
        transform: translateY(-100%);
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    90% {
        opacity: 1;
    }
    100% {
        transform: translateY(100%);
        opacity: 0;
    }
}

@keyframes glitch {
    0% {
        clip-path: inset(40% 0 61% 0);
        transform: translate(-2px, 2px);
    }
    20% {
        clip-path: inset(92% 0 1% 0);
        transform: translate(2px, -2px);
    }
    40% {
        clip-path: inset(43% 0 1% 0);
        transform: translate(-2px, 2px);
    }
    60% {
        clip-path: inset(25% 0 58% 0);
        transform: translate(2px, -2px);
    }
    80% {
        clip-path: inset(54% 0 7% 0);
        transform: translate(-2px, 2px);
    }
    100% {
        clip-path: inset(58% 0 43% 0);
        transform: translate(2px, -2px);
    }
}

/* ============================================
   ANIMATION CLASSES
   ============================================ */

.animate-fade-in {
    animation: fade-in 0.5s ease forwards;
}

.animate-fade-in-up {
    animation: fade-in-up 0.5s ease forwards;
}

.animate-fade-in-down {
    animation: fade-in-down 0.5s ease forwards;
}

.animate-fade-in-left {
    animation: fade-in-left 0.5s ease forwards;
}

.animate-fade-in-right {
    animation: fade-in-right 0.5s ease forwards;
}

.animate-slide-in-left {
    animation: slide-in-left 0.4s ease forwards;
}

.animate-slide-in-right {
    animation: slide-in-right 0.4s ease forwards;
}

.animate-scale-in {
    animation: scale-in 0.3s ease forwards;
}

.animate-scale-out {
    animation: scale-out 0.3s ease forwards;
}

.animate-pulse {
    animation: pulse 2s ease infinite;
}

.animate-pulse-orange {
    animation: pulse-orange 2s ease infinite;
}

.animate-glow {
    animation: glow 2s ease infinite;
}

.animate-glow-text {
    animation: glow-text 2s ease infinite;
}

.animate-border-glow {
    animation: border-glow 2s ease infinite;
}

.animate-spin {
    animation: spin 1s linear infinite;
}

.animate-float {
    animation: float 3s ease infinite;
}

.animate-shake {
    animation: shake 0.5s ease;
}

.animate-typing {
    overflow: hidden;
    white-space: nowrap;
    border-right: 2px solid var(--color-accent-primary);
    animation: 
        typing 3s steps(40, end),
        blink-cursor 0.75s step-end infinite;
}

/* Staggered animations */
.stagger-1 { animation-delay: 0.1s; }
.stagger-2 { animation-delay: 0.2s; }
.stagger-3 { animation-delay: 0.3s; }
.stagger-4 { animation-delay: 0.4s; }
.stagger-5 { animation-delay: 0.5s; }
.stagger-6 { animation-delay: 0.6s; }
.stagger-7 { animation-delay: 0.7s; }
.stagger-8 { animation-delay: 0.8s; }
.stagger-9 { animation-delay: 0.9s; }
.stagger-10 { animation-delay: 1.0s; }

/* ============================================
   CARD HOVER EFFECTS
   ============================================ */

.card-hover-effect {
    transition: all 0.3s ease;
}

.card-hover-effect:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(255, 106, 0, 0.15);
}

/* ============================================
   ISAC LOADER
   ============================================ */

.isac-loader {
    position: relative;
    width: 80px;
    height: 80px;
}

.isac-loader-ring {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 2px solid transparent;
    border-top-color: var(--color-accent-primary);
    border-radius: 50%;
    animation: isac-rotate 1.5s linear infinite;
}

.isac-loader-ring:nth-child(2) {
    width: 60%;
    height: 60%;
    top: 20%;
    left: 20%;
    border-top-color: var(--color-accent-secondary);
    animation-duration: 1s;
    animation-direction: reverse;
}

.isac-loader-ring:nth-child(3) {
    width: 30%;
    height: 30%;
    top: 35%;
    left: 35%;
    border-top-color: var(--color-text-primary);
    animation-duration: 0.8s;
}

.isac-loader-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 8px;
    height: 8px;
    background: var(--color-accent-primary);
    border-radius: 50%;
    animation: isac-pulse 1.5s ease infinite;
}

/* ============================================
   SCANLINE OVERLAY
   ============================================ */

.scanline-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    z-index: 9998;
    overflow: hidden;
}

.scanline-overlay::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: rgba(255, 106, 0, 0.1);
    animation: scanline-move 4s linear infinite;
}

/* ============================================
   GLITCH EFFECT
   ============================================ */

.glitch-effect {
    position: relative;
}

.glitch-effect::before,
.glitch-effect::after {
    content: attr(data-text);
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
}

.glitch-effect:hover::before {
    opacity: 0.8;
    color: #ff0000;
    animation: glitch 0.3s linear infinite;
    z-index: -1;
}

.glitch-effect:hover::after {
    opacity: 0.8;
    color: #00ff00;
    animation: glitch 0.3s linear infinite reverse;
    z-index: -2;
}

/* ============================================
   DATA STREAM EFFECT
   ============================================ */

.data-stream {
    position: relative;
    overflow: hidden;
}

.data-stream::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 20px;
    background: linear-gradient(180deg, transparent, rgba(255, 106, 0, 0.1), transparent);
    animation: data-stream 3s linear infinite;
}

/* ============================================
   ORANGE PULSE BUTTON
   ============================================ */

.btn-pulse {
    position: relative;
    overflow: visible;
}

.btn-pulse::after {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: inherit;
    border: 1px solid var(--color-accent-primary);
    opacity: 0;
    animation: pulse-orange 2s ease infinite;
}

/* ============================================
   PROGRESS ANIMATION
   ============================================ */

.progress-animate {
    animation: progress-shine 2s linear infinite;
}

/* ============================================
   PAGE TRANSITIONS
   ============================================ */

.page-transition-enter {
    opacity: 0;
    transform: translateY(10px);
}

.page-transition-enter-active {
    opacity: 1;
    transform: translateY(0);
    transition: opacity 0.3s ease, transform 0.3s ease;
}

.page-transition-exit {
    opacity: 1;
    transform: translateY(0);
}

.page-transition-exit-active {
    opacity: 0;
    transform: translateY(-10px);
    transition: opacity 0.3s ease, transform 0.3s ease;
}

/* ============================================
   HOVER GLOW
   ============================================ */

.hover-glow {
    transition: box-shadow 0.3s ease;
}

.hover-glow:hover {
    box-shadow: 0 0 20px rgba(255, 106, 0, 0.3);
}

/* ============================================
   BORDER ANIMATION
   ============================================ */

.animated-border {
    position: relative;
}

.animated-border::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--color-accent-primary), transparent);
    animation: border-glow 3s ease infinite;
}

/* ============================================
   REDUCED MOTION
   ============================================ */

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
'''

with open(f"{base_dir}/public/css/animations.css", "w") as f:
    f.write(animations_css)

print("animations.css created!")

# 7. public/js/api.js
api_js = '''/**
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
'''

with open(f"{base_dir}/public/js/api.js", "w") as f:
    f.write(api_js)

print("api.js created!")

# 8. public/js/ui.js
ui_js = '''/**
 * UI Module
 * Handles UI utilities, toast notifications, modals, and common UI operations
 */

/**
 * Toast Notification System
 */
class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }
    
    init() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    }
    
    show(message, type = 'info', title = '') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const toastTitle = title || this.getDefaultTitle(type);
        
        toast.innerHTML = `
            <div class="toast-title">${toastTitle}</div>
            <div class="toast-message">${message}</div>
        `;
        
        this.container.appendChild(toast);
        
        // Auto remove after 4 seconds
        setTimeout(() => {
            toast.classList.add('toast-exit');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 4000);
        
        return toast;
    }
    
    getDefaultTitle(type) {
        const titles = {
            info: 'ISAC NOTIFICATION',
            success: 'MISSION COMPLETE',
            error: 'SYSTEM ERROR',
            warning: 'WARNING'
        };
        return titles[type] || 'NOTIFICATION';
    }
    
    success(message, title) {
        return this.show(message, 'success', title);
    }
    
    error(message, title) {
        return this.show(message, 'error', title);
    }
    
    warning(message, title) {
        return this.show(message, 'warning', title);
    }
    
    info(message, title) {
        return this.show(message, 'info', title);
    }
}

/**
 * Modal System
 */
class ModalManager {
    constructor() {
        this.activeModal = null;
        this.backdrop = null;
    }
    
    open(content, options = {}) {
        this.close();
        
        // Create backdrop
        this.backdrop = document.createElement('div');
        this.backdrop.className = 'modal-backdrop';
        this.backdrop.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: modal-backdrop-in 0.3s ease;
        `;
        
        // Create modal content
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.cssText = `
            background: var(--color-glass);
            border: 1px solid var(--color-glass-border);
            border-radius: var(--border-radius-md);
            padding: var(--spacing-xl);
            max-width: ${options.maxWidth || '500px'};
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            animation: modal-content-in 0.3s ease;
            box-shadow: 0 0 40px rgba(255, 106, 0, 0.2);
        `;
        
        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = `
            position: absolute;
            top: var(--spacing-md);
            right: var(--spacing-md);
            background: none;
            border: none;
            color: var(--color-text-secondary);
            font-size: 1.5rem;
            cursor: pointer;
            transition: color 0.2s ease;
        `;
        closeBtn.onmouseenter = () => closeBtn.style.color = 'var(--color-accent-primary)';
        closeBtn.onmouseleave = () => closeBtn.style.color = 'var(--color-text-secondary)';
        closeBtn.onclick = () => this.close();
        
        modalContent.appendChild(closeBtn);
        
        if (typeof content === 'string') {
            const contentDiv = document.createElement('div');
            contentDiv.innerHTML = content;
            modalContent.appendChild(contentDiv);
        } else if (content instanceof HTMLElement) {
            modalContent.appendChild(content);
        }
        
        this.backdrop.appendChild(modalContent);
        document.body.appendChild(this.backdrop);
        this.activeModal = this.backdrop;
        
        // Close on backdrop click
        this.backdrop.addEventListener('click', (e) => {
            if (e.target === this.backdrop && !options.preventBackdropClose) {
                this.close();
            }
        });
        
        // Close on ESC
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                this.close();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
        
        return modalContent;
    }
    
    close() {
        if (this.activeModal) {
            const content = this.activeModal.querySelector('.modal-content');
            if (content) {
                content.style.animation = 'modal-content-out 0.3s ease forwards';
            }
            setTimeout(() => {
                if (this.activeModal && this.activeModal.parentNode) {
                    this.activeModal.parentNode.removeChild(this.activeModal);
                }
                this.activeModal = null;
            }, 300);
        }
    }
    
    confirm(message, title = 'CONFIRM ACTION') {
        return new Promise((resolve) => {
            const content = document.createElement('div');
            content.innerHTML = `
                <h3 style="font-family: var(--font-display); font-size: 1.1rem; color: var(--color-accent-primary); margin-bottom: var(--spacing-md); text-transform: uppercase; letter-spacing: 2px;">${title}</h3>
                <p style="color: var(--color-text-secondary); margin-bottom: var(--spacing-xl); line-height: 1.6;">${message}</p>
                <div style="display: flex; gap: var(--spacing-md); justify-content: flex-end;">
                    <button class="btn" id="modal-cancel">CANCEL</button>
                    <button class="btn btn-danger" id="modal-confirm">CONFIRM</button>
                </div>
            `;
            
            const modal = this.open(content, { preventBackdropClose: true });
            
            modal.querySelector('#modal-cancel').addEventListener('click', () => {
                this.close();
                resolve(false);
            });
            
            modal.querySelector('#modal-confirm').addEventListener('click', () => {
                this.close();
                resolve(true);
            });
        });
    }
}

/**
 * Loading Screen Manager
 */
class LoadingManager {
    constructor() {
        this.element = null;
        this.progressBar = null;
        this.init();
    }
    
    init() {
        this.element = document.createElement('div');
        this.element.className = 'loading-screen';
        this.element.innerHTML = `
            <div class="loading-logo">DIVISION</div>
            <div class="isac-loader" style="margin-bottom: 24px;">
                <div class="isac-loader-ring"></div>
                <div class="isac-loader-ring"></div>
                <div class="isac-loader-ring"></div>
                <div class="isac-loader-center"></div>
            </div>
            <div class="loading-text">INITIALIZING SYSTEMS...</div>
            <div class="loading-progress">
                <div class="loading-progress-bar"></div>
            </div>
        `;
        document.body.appendChild(this.element);
        this.progressBar = this.element.querySelector('.loading-progress-bar');
    }
    
    setProgress(percent) {
        if (this.progressBar) {
            this.progressBar.style.width = `${percent}%`;
        }
    }
    
    hide() {
        if (this.element) {
            this.setProgress(100);
            setTimeout(() => {
                this.element.classList.add('hidden');
                setTimeout(() => {
                    if (this.element && this.element.parentNode) {
                        this.element.parentNode.removeChild(this.element);
                    }
                }, 500);
            }, 500);
        }
    }
}

/**
 * Time Display
 */
function updateTimeDisplay() {
    const timeElements = document.querySelectorAll('.current-time');
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
    timeElements.forEach(el => {
        el.textContent = timeString;
    });
}

/**
 * Utility Functions
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function formatNumber(num) {
    return num.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, ',');
}

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export singletons
export const toast = new ToastManager();
export const modal = new ModalManager();
export const loading = new LoadingManager();

// Export utilities
export {
    updateTimeDisplay,
    debounce,
    throttle,
    formatNumber,
    generateId,
    escapeHtml
};
'''

with open(f"{base_dir}/public/js/ui.js", "w") as f:
    f.write(ui_js)

print("ui.js created!")

# 9. public/js/player.js
player_js = '''/**
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
                    <div class="player-stat-value">${formatNumber(playerData.firepower)}</div>
                    <div class="player-stat-label">Firepower</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${formatNumber(playerData.toughness)}</div>
                    <div class="player-stat-label">Toughness</div>
                </div>
                <div class="player-stat">
                    <div class="player-stat-value">${formatNumber(playerData.skillPower)}</div>
                    <div class="player-stat-label">Skill Power</div>
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
'''

with open(f"{base_dir}/public/js/player.js", "w") as f:
    f.write(player_js)

print("player.js created!")

# 10. public/js/missions.js
missions_js = '''/**
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
'''

with open(f"{base_dir}/public/js/missions.js", "w") as f:
    f.write(missions_js)

print("missions.js created!")

# 11. public/js/modal.js
modal_js = '''/**
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
'''

with open(f"{base_dir}/public/js/modal.js", "w") as f:
    f.write(modal_js)

print("modal.js created!")

# 13. public/index.html
index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Division Agent Progress Tracker</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Stylesheets -->
    <link rel="stylesheet" href="/css/style.css">
    <link rel="stylesheet" href="/css/animations.css">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="/assets/logo.png">
</head>
<body>
    <div class="app-container">
        <!-- Sidebar Navigation -->
        <aside class="sidebar">
            <div class="sidebar-logo">
                <h1>DIVISION</h1>
                <span>AGENT TRACKER</span>
            </div>
            
            <nav class="sidebar-nav">
                <a href="#" class="nav-item active" data-page="dashboard">
                    <i>u25c8</i>
                    <span class="nav-label">Dashboard</span>
                </a>
                <a href="#" class="nav-item" data-page="missions">
                    <i>U+2694</i>
                    <span class="nav-label">Missions</span>
                    <span class="nav-badge" id="sidebar-mission-count">0</span>
                </a>
                <a href="#" class="nav-item" data-page="timeline">
                    <i>U+25A4</i>
                    <span class="nav-label">Timeline</span>
                </a>
                <a href="#" class="nav-item" data-page="player">
                    <i>U+25C9</i>
                    <span class="nav-label">Player</span>
                </a>
                <a href="#" class="nav-item" data-page="statistics">
                    <i>U+25EB</i>
                    <span class="nav-label">Statistics</span>
                </a>
                <a href="#" class="nav-item" data-page="settings">
                    <i>U+2699</i>
                    <span class="nav-label">Settings</span>
                </a>
            </nav>
            
            <div class="sidebar-footer">
                <div class="version">v1.0.0 // ISAC ONLINE</div>
            </div>
        </aside>
        
        <!-- Top Bar -->
        <header class="topbar">
            <div class="topbar-left">
                <div class="agent-info">
                    <span class="agent-name">Agent</span>
                    <span class="agent-level">LV.1</span>
                    <span class="agent-district">Hudson Yards</span>
                </div>
            </div>
            
            <div class="topbar-center">
                <div class="search-bar">
                    <span class="search-icon">ICON_MAGNIFYING_GLASS</span>
                    <input type="text" id="search-input" placeholder="Search missions, districts...">
                </div>
            </div>
            
            <div class="topbar-right">
                <span class="current-time">00:00:00</span>
            </div>
        </header>
        
        <!-- Main Content Area -->
        <main class="main-content" id="main-content">
            <!-- Content dynamically loaded by JavaScript -->
        </main>
        
        <!-- Right Information Panel -->
        <aside class="right-panel" id="right-panel">
            <!-- Content dynamically loaded by JavaScript -->
        </aside>
    </div>
    
    <!-- Mobile Navigation -->
    <nav class="mobile-nav">
        <a href="#" class="mobile-nav-item active" data-page="dashboard">
            <i>u25c8</i>
            <span>Dash</span>
        </a>
        <a href="#" class="mobile-nav-item" data-page="missions">
            <i>U+2694</i>
            <span>Missions</span>
        </a>
        <a href="#" class="mobile-nav-item" data-page="timeline">
            <i>U+25A4</i>
            <span>Timeline</span>
        </a>
        <a href="#" class="mobile-nav-item" data-page="player">
            <i>U+25C9</i>
            <span>Player</span>
        </a>
        <a href="#" class="mobile-nav-item" data-page="settings">
            <i>U+2699</i>
            <span>Settings</span>
        </a>
    </nav>
    
    <!-- Scanline Overlay -->
    <div class="scanline-overlay"></div>
    
    <!-- Application Scripts -->
    <script type="module" src="/js/app.js"></script>
</body>
</html>'''

with open(f"{base_dir}/public/index.html", "w") as f:
    f.write(index_html)

print("index.html created!")

# Recreate app.js - it seems it wasn't saved properly
app_js = '''/**
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
    setInterval(updateTimeDisplay, 1000);
    
    loading.setProgress(40);
    
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
        }, 500);
        
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
'''

with open(f"{base_dir}/public/js/app.js", "w") as f:
    f.write(app_js)

# Verify again
import os
full_path = os.path.join(base_dir, "public/js/app.js")
if os.path.exists(full_path):
    size = os.path.getsize(full_path)
    print(f"public/js/app.js created successfully! ({size:,} bytes)")
else:
    print("Failed to create app.js")