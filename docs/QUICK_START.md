# Quick Start Guide - MCP-PolyGame-Agent

## Current Status: ? Connected to MCP Inspector

You have successfully:
- ? Installed the project
- ? Started the MCP Server
- ? Connected to MCP Inspector

## Next Steps: Testing and Using Tools

### Step 1: Explore Available Tools

In the MCP Inspector interface, you should see **11 tools** listed in the right panel:

1. `initialize_game` - Initialize a new game
2. `reset_game` - Reset game data
3. `query_game_state` - Query current game state
4. `recall_memory` - Retrieve player history
5. `analyze_suspicion` - Analyze player suspicion
6. `record_event` - Record game events
7. `get_player_relations` - Get player relationships
8. `calculate_action_utility` - Calculate action utilities
9. `detect_wolf_patterns` - Detect suspicious patterns
10. `get_server_config` - Get server configuration
11. `greeting_tool` - Greeting tool

### Step 2: Test Basic Workflow

Follow this sequence to test a complete game reasoning workflow:

#### 2.1 Initialize a Game

Click on `initialize_game` tool and enter:

```json
{
  "game_id": "demo_game_001",
  "player_ids": ["Alice", "Bob", "Charlie", "David", "Eve"],
  "total_wolves": 2
}
```

Click **Call Tool** and check the result. You should see:
- Game initialized successfully
- All players added to the system
- Bayesian priors initialized

#### 2.2 Record Game Events

Record some game events to build history:

**Event 1 - Alice speaks:**
```json
{
  "round_num": 1,
  "speaker": "Alice",
  "content": "I think Bob is suspicious, he voted strangely",
  "action_type": "speak",
  "game_id": "demo_game_001",
  "target_player": "Bob",
  "relation_type": "attack"
}
```

**Event 2 - Bob responds:**
```json
{
  "round_num": 1,
  "speaker": "Bob",
  "content": "Alice is lying, I saw nothing suspicious",
  "action_type": "speak",
  "game_id": "demo_game_001",
  "target_player": "Alice",
  "relation_type": "attack"
}
```

**Event 3 - Charlie supports Alice:**
```json
{
  "round_num": 1,
  "speaker": "Charlie",
  "content": "I agree with Alice, Bob seems suspicious",
  "action_type": "speak",
  "game_id": "demo_game_001",
  "target_player": "Bob",
  "relation_type": "attack"
}
```

#### 2.3 Analyze Suspicion

Use Bayesian inference to analyze Bob's suspicion:

```json
{
  "player_id": "Bob",
  "evidence_score": 0.7,
  "evidence_type": "contradiction",
  "description": "Multiple players attacked Bob, and he contradicted himself",
  "game_id": "demo_game_001"
}
```

Check the result - you should see:
- Previous suspicion score
- Updated suspicion score (should be higher)
- Evidence count

#### 2.4 Recall Memory

Retrieve Alice's history:

```json
{
  "player_id": "Alice",
  "game_id": "demo_game_001",
  "limit": 10
}
```

This uses RAG algorithm to retrieve relevant historical records.

#### 2.5 Get Player Relations

Analyze Alice's relationship network:

```json
{
  "player_id": "Alice"
}
```

This uses knowledge graph to show:
- Incoming relations (who attacked/supported Alice)
- Outgoing relations (who Alice attacked/supported)
- Centrality score

#### 2.6 Detect Wolf Patterns

Find suspicious patterns:

```json
{
  "threshold": 0.6
}
```

This will detect:
- Suspicious pairs (potential wolf teams)
- Collusion scores
- Attack network

#### 2.7 Calculate Action Utility

If you're playing as the Seer, calculate which player to check:

```json
{
  "action_candidates": [
    {"type": "check", "target": "Bob"},
    {"type": "check", "target": "Charlie"},
    {"type": "check", "target": "David"}
  ],
  "current_role": "seer",
  "alive_count": 5,
  "suspicion_scores": {
    "Bob": 0.75,
    "Charlie": 0.4,
    "David": 0.5,
    "Eve": 0.3
  }
}
```

This uses game tree search to recommend the best action.

#### 2.8 Query Game State

Check current game status:

```json
{
  "game_id": "demo_game_001"
}
```

### Step 3: Complete Game Scenario

Try this complete scenario simulating a game round:

1. **Initialize**: Create game with 5 players
2. **Round 1 - Day Phase**:
   - Record 3-4 speaking events with attacks/supports
   - Analyze suspicion for each mentioned player
3. **Round 1 - Night Phase** (if you're Seer):
   - Use `calculate_action_utility` to decide who to check
   - Record the check action
4. **Round 2 - Analysis**:
   - Use `get_player_relations` to find patterns
   - Use `detect_wolf_patterns` to identify suspicious pairs
   - Use `recall_memory` to review key player statements
5. **Decision Making**:
   - Use `calculate_action_utility` for voting decisions
   - Record voting events

### Step 4: Advanced Usage

#### Using with LLM (Claude/ChatGPT)

The MCP Server is designed to work with LLMs. The LLM can:
- Call tools automatically based on game context
- Use tool results to make decisions
- Chain multiple tools together

Example LLM prompt:
```
"You are playing Werewolf as the Seer. 
Current game state: [use query_game_state]
Recent events: [use recall_memory]
Who should you check tonight? Use calculate_action_utility to decide."
```

#### Monitoring Logs

Check the `logs/` directory to see:
- All tool calls with parameters
- Algorithm state changes
- Database operations
- Detailed debugging information

### Step 5: Integration

#### With Claude Desktop

1. Edit Claude Desktop config (see README)
2. Restart Claude Desktop
3. Ask Claude to help you play Werewolf
4. Claude will automatically use the MCP tools

#### With Custom Python Script

See `test_mcp_tools.py` for example of programmatic tool usage.

## Tips

1. **Start Simple**: Begin with `initialize_game` and `record_event`
2. **Build History**: Record multiple events before analyzing
3. **Check Results**: Always verify tool outputs make sense
4. **Use Logs**: Check logs/ directory for detailed information
5. **Experiment**: Try different evidence scores and thresholds

## Common Workflows

### Workflow 1: Initial Game Setup
```
initialize_game ¡ú record_event (multiple) ¡ú query_game_state
```

### Workflow 2: Player Analysis
```
recall_memory ¡ú analyze_suspicion ¡ú get_player_relations
```

### Workflow 3: Decision Making
```
query_game_state ¡ú calculate_action_utility ¡ú record_event
```

### Workflow 4: Pattern Detection
```
record_event (multiple rounds) ¡ú detect_wolf_patterns ¡ú get_player_relations
```

## Next Steps

1. ? Test all tools individually
2. ? Run a complete game scenario
3. ? Integrate with Claude Desktop or other LLM
4. ? Build custom game logic using the tools
5. ? Analyze real game data

Enjoy exploring the MCP-PolyGame-Agent! ?
