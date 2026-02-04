# shaziwzy
wzy is a shazi

## Features
- 🌳 Game tree search for optimal action selection
- 🔍 RAG-based memory retrieval system
- 📝 Comprehensive logging system
- 🤖 **New: Machine learning model training and management framework**

## System Requirements
- Python 3.6 or higher
- A compatible database system (SQLite, PostgreSQL, etc.)
- A machine with sufficient memory and processing power

## Example Usage

### 1. Initialize a Game
```bash
python server.py
```

### 2. Play a Game
```bash
python game.py
```

## Project Structure

```
YA_MCPServer_Template/
├── core/                    # Core algorithm modules
│   ├── data/                # **New: Data collection and preprocessing**
│   ├── models/              # **New: Model definitions and management**
│   ├── training/            # **New: Training loops and utilities**
│   ├── evaluation/          # **New: Model evaluation and metrics**
│   ├── database.py          # SQLite database management
│   ├── bayesian_inference.py # Bayesian inference algorithm
│   ├── knowledge_graph.py   # Knowledge graph algorithm
│   └── game_tree.py         # Game tree search algorithm
├── tools/                   # MCP tools
│   ├── game_init.py         # Game initialization tools
│   ├── game_tools.py        # Core game tools
│   └── training_tools.py    # **New: Tools for ML model training**
├── modules/                 # Common modules
├── config.yaml              # Server configuration
├── server.py                # Main server file
├── requirements.txt         # Python dependencies
└── test_mcp_tools.py        # Test script
```

## Database

The SQLite database is automatically created at `data/game.db` on first run. It contains:

- **GameHistory**: All game events and actions
- **PlayerProfile**: Player suspicion scores and profiles
- **GameState**: Current game state information
- **TrainingData**: **New:** Stores training samples (features and labels)
- **ModelVersion**: **New:** Tracks different versions of trained models
- **TrainingRun**: **New:** Logs the history and results of training sessions

## Logging

Logs are stored in the `logs/` directory with:
- `game.log`: Game events and actions
- `training.log`: Training sessions and model performance
- `evaluation.log`: Model evaluation results

## Machine Learning Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `start_training` | Start a model training session in the background | `model_type` |
| `get_training_status` | Check the status of a training session | `run_id` |
| `stop_training` | Send a stop signal to a running training session | `run_id` |
| `evaluate_model` | Evaluate a trained model on the test dataset | `model_version_id` |
| `get_model_metrics` | Retrieve performance metrics for a specific model | `model_version_id` |
| `compare_models` | Compare metrics between different model versions | `version_ids` |

## Example Usage

### 1. Initialize a Game
```bash
python server.py
```

### 2. Play a Game
```bash
python game.py
```

## Contributors

| Name | Student ID | Role | Notes |
| :--: | :--------: | :--: | :---: |
| haaland0325 | (Your ID)  | Lead Developer | Implemented core logic and ML pipeline |

## References
