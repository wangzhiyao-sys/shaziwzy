# Resources and Prompts Usage Guide

## Overview

MCP-PolyGame-Agent provides **Resources** (data access) and **Prompts** (pre-built analysis templates) to help you use the system more effectively.

## Resources

Resources allow you to access game data and documentation directly.

### Available Resources

#### 1. Game State Resource
**URI**: `game://game_state/{game_id}`

Get current game state including alive players, round number, and status.

**Usage Example**:
```
Access: game://game_state/demo_game_001
```

**Returns**: JSON with game state information

#### 2. Player Profile Resource
**URI**: `game://player_profile/{player_id}`

Get player profile including suspicion score, assumed role, and personality.

**Usage Example**:
```
Access: game://player_profile/Alice
```

**Returns**: JSON with player profile data

#### 3. Game History Resource
**URI**: `game://game_history/{game_id}`

Get game history, optionally filtered by round.

**Usage Example**:
```
Access: game://game_history/demo_game_001
```

**Returns**: JSON with game history records

#### 4. Game Usage Guide
**URI**: `file:///docs/GAME_USAGE.md`

Access the complete usage guide documentation.

**Usage Example**:
```
Access: file:///docs/GAME_USAGE.md
```

**Returns**: Markdown documentation

#### 5. Quick Start Guide
**URI**: `file:///docs/QUICK_START.md`

Access the quick start guide.

**Usage Example**:
```
Access: file:///docs/QUICK_START.md
```

**Returns**: Quick start instructions

#### 6. README File
**URI**: `file:///README.md`

Access the project README.

**Usage Example**:
```
Access: file:///README.md
```

**Returns**: README content

#### 7. Server Logs
**URI**: `file:///logs/{path}`

Access server log files for debugging.

**Usage Example**:
```
Access: file:///logs/2026-01-24_11-13-35.log
```

**Returns**: Log file content

## Prompts

Prompts are pre-built analysis templates that generate comprehensive guidance based on current game state.

### Available Prompts

#### 1. Analyze Game Situation
**Name**: `analyze_game_situation`

Generate a comprehensive analysis of the current game situation.

**Parameters**:
- `game_id` (required): The game identifier
- `current_role` (optional): Your current role (default: "seer")
- `focus_player` (optional): Player to focus analysis on

**Usage Example**:
```json
{
  "game_id": "demo_game_001",
  "current_role": "seer",
  "focus_player": "Bob"
}
```

**Returns**: Detailed analysis including:
- Current game state
- Player suspicion scores
- Recent events
- Relationship information
- Recommended actions

**When to Use**:
- At the start of each round
- When you need a comprehensive overview
- Before making important decisions

#### 2. Decision Making Guide
**Name**: `decision_making_guide`

Generate a decision-making prompt for choosing the best action.

**Parameters**:
- `game_id` (required): The game identifier
- `current_role` (required): Your current role
- `action_type` (optional): Type of action (check, vote, speak) - default: "check"

**Usage Example**:
```json
{
  "game_id": "demo_game_001",
  "current_role": "seer",
  "action_type": "check"
}
```

**Returns**: Decision-making guide with:
- Current situation analysis
- Action-specific recommendations
- Tool usage examples
- Recommended workflow

**When to Use**:
- When you need to make a decision (check, vote, etc.)
- When evaluating multiple options
- Before taking critical actions

#### 3. Player Investigation
**Name**: `player_investigation`

Generate an investigation prompt for analyzing a specific player.

**Parameters**:
- `game_id` (required): The game identifier
- `player_id` (required): The player to investigate

**Usage Example**:
```json
{
  "game_id": "demo_game_001",
  "player_id": "Bob"
}
```

**Returns**: Comprehensive investigation report including:
- Player profile
- Historical actions
- Relationship network
- Investigation steps
- Key questions to consider

**When to Use**:
- When a player seems suspicious
- Before voting someone out
- When analyzing player behavior
- To understand player relationships

#### 4. Game Strategy Guide
**Name**: `game_strategy_guide`

Generate a comprehensive strategy guide based on your role.

**Parameters**:
- `game_id` (required): The game identifier
- `current_role` (required): Your current role

**Usage Example**:
```json
{
  "game_id": "demo_game_001",
  "current_role": "seer"
}
```

**Returns**: Role-specific strategy guide with:
- Current game state
- Role-specific strategies
- Critical game phase guidance
- Recommended tool sequences

**When to Use**:
- At the start of the game
- When you're unsure what to do
- To learn role-specific strategies
- For strategic planning

#### 5. Greeting Prompt
**Name**: `greet_user`

Generate a greeting message (for testing).

**Parameters**:
- `name` (required): Your name

**Usage Example**:
```json
{
  "name": "Alice"
}
```

## How to Use in MCP Inspector

### Using Resources

1. Go to the **Resources** tab in MCP Inspector
2. You'll see a list of available resources
3. Click on a resource to view its details
4. Enter the required parameters (for parameterized resources)
5. The resource content will be displayed

### Using Prompts

1. Go to the **Prompts** tab in MCP Inspector
2. You'll see a list of available prompts
3. Click on a prompt to view its details
4. Enter the required parameters
5. The generated prompt/analysis will be displayed
6. You can use this output to guide your tool usage

## Workflow Examples

### Example 1: Starting a New Round

1. Use **Resource**: `game://game_state/{game_id}` to get current state
2. Use **Prompt**: `analyze_game_situation` to get comprehensive analysis
3. Use **Prompt**: `game_strategy_guide` to get role-specific strategy
4. Use **Tools**: Based on the prompts, call appropriate tools

### Example 2: Investigating a Suspicious Player

1. Use **Resource**: `game://player_profile/{player_id}` to get profile
2. Use **Resource**: `game://game_history/{game_id}` to get history
3. Use **Prompt**: `player_investigation` to get investigation guide
4. Use **Tools**: Follow the investigation steps from the prompt

### Example 3: Making a Decision

1. Use **Prompt**: `decision_making_guide` with your action type
2. Review the recommended workflow
3. Use **Tools**: Follow the tool sequence suggested
4. Make your decision based on the results

## Tips

1. **Use Prompts First**: Prompts provide structured guidance - use them before diving into tools
2. **Combine Resources and Prompts**: Use resources to get data, then prompts to analyze it
3. **Follow the Workflows**: Prompts include recommended tool sequences - follow them
4. **Review Documentation**: Use the documentation resources when you need reference
5. **Check Logs**: Use log resources to debug issues

## Integration with LLMs

When using with Claude Desktop or other LLMs:

- LLMs can automatically access resources when needed
- Prompts provide context for LLMs to understand the game state
- LLMs can use prompt outputs to generate tool calls
- Resources provide real-time data for LLM reasoning

Example LLM conversation:
```
User: "I'm the Seer in round 2. What should I do?"

LLM: [Uses analyze_game_situation prompt]
     [Uses decision_making_guide prompt]
     [Calls calculate_action_utility tool]
     [Provides recommendation]
```

Enjoy using Resources and Prompts to enhance your game reasoning! ?
