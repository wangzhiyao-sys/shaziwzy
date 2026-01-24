<<<<<<< HEAD
# MCP-PolyGame-Agent

A Model Context Protocol (MCP) Server for role-aware multi-party game reasoning, designed for simplified Werewolf game scenarios (5 players: 2 wolves, 2 villagers, 1 seer).

## Project Overview

This MCP Server provides intelligent game reasoning capabilities through three core algorithms:

1. **Bayesian Inference** - For identity reasoning and suspicion analysis
2. **Knowledge Graph** - For relationship analysis and pattern detection
3. **Game Tree Search** - For action utility calculation and decision making

## Features

- 🎮 Game state management with SQLite database
- 🧠 Bayesian inference for player suspicion scoring
- 📊 Knowledge graph for relationship analysis
- 🌳 Game tree search for optimal action selection
- 🔍 RAG-based memory retrieval system
- 📝 Comprehensive logging system

## System Requirements

- **Python**: >= 3.10
- **Operating System**: Windows / Linux / macOS
- **Package Manager**: pip or conda (recommended)

## Installation Guide

### Step 1: Clone or Download the Project

```powershell
# If using git
git clone <repository-url>
cd YA_MCPServer_Template

# Or extract the project to your desired location
```

### Step 2: Create Conda Environment (Recommended)

```powershell
# Create a new conda environment with Python 3.10 or higher
conda create -n mcp-polygame python=3.10 -y

# Activate the environment
conda activate mcp-polygame
```

**Alternative: Using Python venv**

```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate
```

### Step 3: Install Dependencies

Navigate to the project directory:

```powershell
cd "C:\path\to\YA_MCPServer_Template"
```

Install dependencies using pip:

```powershell
pip install -r requirements.txt
```

Or install in editable mode:

```powershell
pip install -e .
```

### Step 4: Verify Installation

Test if all modules can be imported:

```powershell
python -c "from core.database import GameDatabase; from core.bayesian_inference import BayesianInference; print('Installation successful!')"
```

## Running the Server

### Start the MCP Server

```powershell
# Make sure you're in the conda environment
conda activate mcp-polygame

# Navigate to project directory
cd "C:\path\to\YA_MCPServer_Template"

# Start the server
python server.py
```

You should see output like:

```
2026-01-24 11:13:35 | INFO | MCP-PolyGame-Agent:start:126 - Starting MCP server: MCP-PolyGame-Agent
INFO:     Uvicorn running on http://127.0.0.1:12345 (Press CTRL+C to quit)
```

The server is now running on `http://127.0.0.1:12345` via SSE transport.

## Usage

### Method 1: Using MCP Inspector (Recommended for Testing)

#### Prerequisites

Install Node.js (if not already installed):

**Windows:**
```powershell
winget install OpenJS.NodeJS.LTS
```

Or download from: https://nodejs.org/

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**macOS:**
```bash
brew install node
```

#### Start MCP Inspector

1. **Keep the server running** in the first terminal

2. **Open a new terminal** and run:

```powershell
conda activate mcp-polygame
cd "C:\path\to\YA_MCPServer_Template"
mcp dev server.py
```

3. **In the browser** that opens:
   - Select transport type: **sse**
   - Enter server URL: `http://127.0.0.1:12345`
   - Click **Connect**

4. **Test tools** in the right panel by:
   - Clicking on tool names to see details
   - Entering parameters
   - Clicking "Call Tool" to execute
   - Viewing results

### Method 2: Using Python Test Script

A test script is provided to quickly verify all tools:

```powershell
# Make sure server is running in another terminal
conda activate mcp-polygame
cd "C:\path\to\YA_MCPServer_Template"
python test_mcp_tools.py
```

This will test all available tools and display results.

### Method 3: Using Claude Desktop

1. **Edit Claude Desktop configuration** (usually at):
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Add MCP Server configuration**:

```json
{
  "mcpServers": {
    "MCP-PolyGame-Agent": {
      "url": "http://127.0.0.1:12345"
    }
  }
}
```

3. **Restart Claude Desktop** to connect to the server.

## Available Tools

### Game Initialization

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `initialize_game` | Initialize a new game session | `game_id`, `player_ids`, `total_wolves` |
| `reset_game` | Reset all game data | `game_id` (optional) |

### Game State Management

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `query_game_state` | Get current game state | `game_id` |
| `record_event` | Record a game event | `round_num`, `speaker`, `content`, `action_type` |

### Analysis Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `recall_memory` | Retrieve player history (RAG) | `player_id`, `game_id`, `limit` |
| `analyze_suspicion` | Analyze suspicion (Bayesian) | `player_id`, `evidence_score`, `evidence_type` |
| `get_player_relations` | Get relationship network | `player_id` |
| `detect_wolf_patterns` | Detect suspicious patterns | `threshold` |
| `calculate_action_utility` | Calculate action utilities | `action_candidates`, `current_role`, `suspicion_scores` |

## Example Usage

### 1. Initialize a Game

```python
# Using MCP Inspector or Python client
initialize_game(
    game_id="game_001",
    player_ids=["player1", "player2", "player3", "player4", "player5"],
    total_wolves=2
)
```

### 2. Record Game Events

```python
record_event(
    round_num=1,
    speaker="player1",
    content="I think player2 is suspicious",
    action_type="speak",
    game_id="game_001",
    target_player="player2",
    relation_type="attack"
)
```

### 3. Analyze Player Suspicion

```python
analyze_suspicion(
    player_id="player2",
    evidence_score=0.7,
    evidence_type="contradiction",
    description="Contradicted previous statement",
    game_id="game_001"
)
```

### 4. Calculate Action Utility

```python
calculate_action_utility(
    action_candidates=[
        {"type": "check", "target": "player2"},
        {"type": "check", "target": "player3"}
    ],
    current_role="seer",
    alive_count=5,
    suspicion_scores={
        "player2": 0.7,
        "player3": 0.3,
        "player4": 0.5,
        "player5": 0.4
    }
)
```

## Project Structure

```
YA_MCPServer_Template/
├── core/                    # Core algorithm modules
│   ├── database.py         # SQLite database management
│   ├── bayesian_inference.py # Bayesian inference algorithm
│   ├── knowledge_graph.py   # Knowledge graph algorithm
│   └── game_tree.py         # Game tree search algorithm
├── tools/                   # MCP tools
│   ├── game_init.py         # Game initialization tools
│   └── game_tools.py        # Core game tools
├── modules/                 # Common modules
├── config.yaml             # Server configuration
├── server.py               # Main server file
├── requirements.txt        # Python dependencies
└── test_mcp_tools.py       # Test script
```

## Database

The SQLite database is automatically created at `data/game.db` on first run. It contains:

- **GameHistory**: All game events and actions
- **PlayerProfile**: Player suspicion scores and profiles
- **GameState**: Current game state information

## Logging

Logs are stored in the `logs/` directory with:
- Automatic rotation (10 MB per file)
- Retention (7 days)
- Compression (ZIP format)

## Configuration

Edit `config.yaml` to customize:

- Server name and metadata
- Transport type (stdio or sse)
- Host and port (for SSE mode)
- Logging settings

## Troubleshooting

### Issue: "uv not found" or "npx not found"

**Solution**: Install Node.js (see Method 1 prerequisites) or use the Python test script instead.

### Issue: "ModuleNotFoundError"

**Solution**: Make sure you've activated the conda environment and installed dependencies:
```powershell
conda activate mcp-polygame
pip install -r requirements.txt
```

### Issue: "Port already in use"

**Solution**: Change the port in `config.yaml` or stop the process using port 12345.

### Issue: "Database locked"

**Solution**: Make sure only one instance of the server is running at a time.

## Development

### Code Style

The project uses:
- **Black** for code formatting
- **Ruff** for linting

### Adding New Tools

1. Create a new function in `tools/` directory
2. Use the `@YA_MCPServer_Tool` decorator
3. The tool will be automatically registered

### Adding New Algorithms

1. Create a new module in `core/` directory
2. Import and use in tool functions
3. Update documentation

## License

[Add your license information here]

## Contributors

| Name | Student ID | Role | Notes |
| :--: | :--------: | :--: | :---: |
|      |            |      |       |

## References

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- Project documentation in `docs/` directory
=======
# shaziwzy
wzy is a shazi
>>>>>>> 4d5ec29d2fe52cc6db9484b94fb408751f3746bc
