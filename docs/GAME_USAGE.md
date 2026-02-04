# MCP-PolyGame-Agent Usage Guide

## Overview

MCP-PolyGame-Agent is an MCP Server that provides game reasoning capabilities for a 5-player simplified Werewolf game (2 wolves, 2 villagers, 1 seer). It uses three core algorithms:

1. **Bayesian Inference** - For identity reasoning
2. **Knowledge Graph** - For relationship analysis
3. **Game Tree Search** - For action decision making

## Core Algorithms

### 1. Bayesian Inference (`core/bayesian_inference.py`)

Maintains probability matrices for each player. Updates posterior probabilities when evidence is found.

- `initialize_priors()`: Initialize prior probabilities for all players
- `update_suspicion()`: Update suspicion score based on evidence
- `analyze_contradiction()`: Detect contradictions in player statements

### 2. Knowledge Graph (`core/knowledge_graph.py`)

Builds a graph structure where nodes are players and edges represent relationships (attack, support, etc.).

- `add_node()`: Add a player node
- `add_edge()`: Add a relationship edge
- `get_player_relations()`: Get all relations for a player
- `detect_wolf_pair()`: Detect suspicious pairs
- `detect_collusion()`: Detect collusion patterns

### 3. Game Tree Search (`core/game_tree.py`)

Uses minimax-like algorithm to evaluate action utilities.

- `calculate_action_utility()`: Calculate utility scores for actions
- `minimax_decision()`: Minimax search for optimal action

## Database Schema

### GameHistory Table
- `id`: Primary key
- `round_num`: Round number
- `speaker`: Player ID
- `content`: Action content
- `action_type`: Type of action (speak, vote, check)
- `timestamp`: Event timestamp
- `game_id`: Game session ID

### PlayerProfile Table
- `player_id`: Primary key
- `role_assumed`: Assumed role
- `suspicion_score`: Suspicion score (0.0-1.0)
- `personality`: Player personality
- `game_id`: Game session ID
- `updated_at`: Last update timestamp

### GameState Table
- `game_id`: Primary key
- `current_round`: Current round number
- `alive_players`: Comma-separated list of alive players
- `game_status`: Game status
- `updated_at`: Last update timestamp

## MCP Tools

### Game Initialization

#### `initialize_game`
Initialize a new game session.

**Parameters:**
- `game_id` (str): Unique game identifier
- `player_ids` (List[str]): List of player IDs
- `total_wolves` (int): Number of wolves (default: 2)

**Returns:**
- Game initialization status

#### `reset_game`
Reset all game data and algorithms.

**Parameters:**
- `game_id` (Optional[str]): Game ID to reset

**Returns:**
- Reset status

### Game State Management

#### `query_game_state`
Get current game state.

**Parameters:**
- `game_id` (str): Game identifier

**Returns:**
- Current round, alive players, game status

#### `record_event`
Record a game event to database.

**Parameters:**
- `round_num` (int): Round number
- `speaker` (str): Player ID
- `content` (str): Event content
- `action_type` (str): Type of action
- `game_id` (Optional[str]): Game ID
- `target_player` (Optional[str]): Target player ID
- `relation_type` (Optional[str]): Relation type for knowledge graph

**Returns:**
- Event recording status

### Memory and Analysis

#### `recall_memory`
Retrieve historical statements using RAG algorithm.

**Parameters:**
- `player_id` (str): Player ID
- `game_id` (Optional[str]): Game ID filter
- `round_num` (Optional[int]): Round filter
- `action_type` (Optional[str]): Action type filter
- `limit` (int): Maximum records (default: 10)

**Returns:**
- Historical records and summary

#### `analyze_suspicion`
Analyze player suspicion using Bayesian inference.

**Parameters:**
- `player_id` (str): Player ID
- `evidence_score` (float): Evidence score (0.0-1.0)
- `evidence_type` (str): Type of evidence
- `description` (str): Evidence description
- `game_id` (Optional[str]): Game ID

**Returns:**
- Previous and current suspicion scores

### Relationship Analysis

#### `get_player_relations`
Get relationship network for a player.

**Parameters:**
- `player_id` (str): Player ID

**Returns:**
- Incoming/outgoing relations and centrality score

#### `detect_wolf_patterns`
Detect suspicious patterns in relationships.

**Parameters:**
- `threshold` (float): Detection threshold (default: 0.7)

**Returns:**
- Suspicious pairs, collusion scores, attack network

### Decision Making

#### `calculate_action_utility`
Calculate utility scores for possible actions.

**Parameters:**
- `action_candidates` (List[Dict]): List of action dictionaries
- `current_role` (str): Current player role
- `alive_count` (int): Number of alive players
- `suspicion_scores` (Dict[str, float]): Suspicion scores

**Returns:**
- Actions with utility scores and recommendations

## Usage Example

1. Initialize a game:
```python
initialize_game(
    game_id="game_001",
    player_ids=["player1", "player2", "player3", "player4", "player5"],
    total_wolves=2
)
```

2. Record events:
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

3. Analyze suspicion:
```python
analyze_suspicion(
    player_id="player2",
    evidence_score=0.7,
    evidence_type="contradiction",
    description="Contradicted previous statement",
    game_id="game_001"
)
```

4. Calculate action utility:
```python
calculate_action_utility(
    action_candidates=[
        {"type": "check", "target": "player2"},
        {"type": "check", "target": "player3"}
    ],
    current_role="seer",
    alive_count=5,
    suspicion_scores={"player2": 0.7, "player3": 0.3}
)
```

## Logging

All tool calls are logged with detailed information including:
- Input parameters
- Output results
- Algorithm state changes
- Database operations

Logs are stored in the `logs/` directory with rotation and compression.

## Database Location

The SQLite database is stored at `data/game.db` by default. The directory is created automatically if it doesn't exist.
