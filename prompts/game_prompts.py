import json
from typing import Any, Dict
from prompts import YA_MCPServer_Prompt
from core.database import GameDatabase
from core.bayesian_inference import BayesianInference
from core.knowledge_graph import KnowledgeGraph
from modules.YA_Common.utils.logger import get_logger

logger = get_logger("game_prompts")

db = GameDatabase()
bayesian = BayesianInference()
knowledge_graph = KnowledgeGraph()


@YA_MCPServer_Prompt(
    name="analyze_game_situation",
    title="Analyze Game Situation",
    description="Generate a comprehensive analysis prompt for the current game situation, including suspicion scores, relationships, and recommended actions"
)
async def analyze_game_situation_prompt(
    game_id: str,
    current_role: str = "seer",
    focus_player: str = None
) -> str:
    """
    Generate a prompt for analyzing the current game situation.
    
    Args:
        game_id: The game identifier
        current_role: Current role of the player (seer, villager, etc.)
        focus_player: Optional player to focus analysis on
        
    Returns:
        A detailed analysis prompt string
    """
    try:
        game_state = db.get_game_state(game_id)
        if not game_state:
            return f"Game {game_id} not found. Please initialize the game first."
        
        alive_players = game_state.get("alive_players", [])
        current_round = game_state.get("current_round", 1)
        
        # Get all player profiles
        profiles = db.get_all_player_profiles(game_id=game_id)
        suspicion_scores = {
            p["player_id"]: p.get("suspicion_score", 0.0)
            for p in profiles
            if p["player_id"] in alive_players
        }
        
        # Get recent history
        recent_history = db.get_game_history(game_id=game_id, limit=10)
        
        # Build analysis prompt
        prompt = f"""# Game Situation Analysis - Round {current_round}

## Current Role: {current_role}
## Alive Players: {', '.join(alive_players)}

## Player Suspicion Scores:
"""
        for player_id, score in sorted(suspicion_scores.items(), key=lambda x: x[1], reverse=True):
            prompt += f"- **{player_id}**: {score:.2f} ({'High' if score > 0.7 else 'Medium' if score > 0.4 else 'Low'} suspicion)\n"
        
        if recent_history:
            prompt += f"\n## Recent Events (Last {len(recent_history)}):\n"
            for event in recent_history[-5:]:
                prompt += f"- **Round {event['round_num']}** - {event['speaker']} ({event['action_type']}): {event['content'][:100]}\n"
        
        if focus_player:
            relations = knowledge_graph.get_player_relations(focus_player)
            prompt += f"\n## Focus Player: {focus_player}\n"
            if relations.get("outgoing"):
                prompt += f"**Attacks/Supports**: {len(relations['outgoing'])} outgoing relations\n"
            if relations.get("incoming"):
                prompt += f"**Attacked/Supported by**: {len(relations['incoming'])} incoming relations\n"
        
        prompt += f"""
## Recommended Actions:
1. Use `recall_memory` to review key player statements
2. Use `analyze_suspicion` to update suspicion scores based on new evidence
3. Use `get_player_relations` to analyze relationship patterns
4. Use `calculate_action_utility` to determine optimal action
5. Use `detect_wolf_patterns` to identify suspicious pairs

## Next Steps:
Based on your role as {current_role}, consider:
- If you're the Seer: Use `calculate_action_utility` to decide who to check
- If you're a Villager: Use `analyze_suspicion` and `get_player_relations` to identify threats
- Record important events with `record_event` to build the knowledge graph
"""
        
        return prompt
    except Exception as e:
        logger.error(f"Error generating analysis prompt: {e}")
        return f"Error generating analysis: {str(e)}"


@YA_MCPServer_Prompt(
    name="decision_making_guide",
    title="Decision Making Guide",
    description="Generate a decision-making prompt for choosing the best action based on current game state"
)
async def decision_making_guide_prompt(
    game_id: str,
    current_role: str,
    action_type: str = "check"
) -> str:
    """
    Generate a prompt for decision making.
    
    Args:
        game_id: The game identifier
        current_role: Current role of the player
        action_type: Type of action to make (check, vote, speak)
        
    Returns:
        A decision-making prompt string
    """
    try:
        game_state = db.get_game_state(game_id)
        if not game_state:
            return f"Game {game_id} not found."
        
        alive_players = game_state.get("alive_players", [])
        current_round = game_state.get("current_round", 1)
        
        profiles = db.get_all_player_profiles(game_id=game_id)
        suspicion_scores = {
            p["player_id"]: p.get("suspicion_score", 0.0)
            for p in profiles
            if p["player_id"] in alive_players
        }
        
        prompt = f"""# Decision Making Guide - {action_type.upper()}

## Current Situation:
- **Role**: {current_role}
- **Round**: {current_round}
- **Alive Players**: {len(alive_players)} ({', '.join(alive_players)})

## Current Suspicion Scores:
"""
        for player_id, score in sorted(suspicion_scores.items(), key=lambda x: x[1], reverse=True):
            prompt += f"- {player_id}: {score:.2f}\n"
        
        if action_type == "check":
            prompt += f"""
## As the Seer, you should:
1. Use `calculate_action_utility` with action_type="check" to evaluate each player
2. Consider players with high suspicion scores (>0.6)
3. Also consider players with low suspicion scores who might be hiding
4. Check the utility scores to make an informed decision

Example tool call:
```json
{{
  "action_candidates": [
    {{"type": "check", "target": "player1"}},
    {{"type": "check", "target": "player2"}}
  ],
  "current_role": "{current_role}",
  "alive_count": {len(alive_players)},
  "suspicion_scores": {json.dumps(suspicion_scores, indent=2)}
}}
```
"""
        elif action_type == "vote":
            prompt += f"""
## Voting Decision:
1. Use `calculate_action_utility` with action_type="vote" to evaluate each player
2. Consider elimination value and risk factors
3. Focus on players with highest suspicion scores
4. Consider game state (if only 3 players left, be very careful)

Example tool call:
```json
{{
  "action_candidates": [
    {{"type": "vote", "target": "player1"}},
    {{"type": "vote", "target": "player2"}}
  ],
  "current_role": "{current_role}",
  "alive_count": {len(alive_players)},
  "suspicion_scores": {json.dumps(suspicion_scores, indent=2)}
}}
```
"""
        else:
            prompt += f"""
## Action Decision:
1. Review recent events with `recall_memory`
2. Analyze relationships with `get_player_relations`
3. Update suspicion scores with `analyze_suspicion` if needed
4. Use `calculate_action_utility` to evaluate options
"""
        
        prompt += f"""
## Recommended Workflow:
1. Query current game state: `query_game_state` (game_id: "{game_id}")
2. Review player memories: `recall_memory` for key players
3. Calculate action utilities: `calculate_action_utility`
4. Make decision based on highest utility score
5. Record your action: `record_event`
"""
        
        return prompt
    except Exception as e:
        logger.error(f"Error generating decision prompt: {e}")
        return f"Error generating decision guide: {str(e)}"


@YA_MCPServer_Prompt(
    name="player_investigation",
    title="Player Investigation",
    description="Generate an investigation prompt for analyzing a specific player's behavior and relationships"
)
async def player_investigation_prompt(
    game_id: str,
    player_id: str
) -> str:
    """
    Generate a prompt for investigating a specific player.
    
    Args:
        game_id: The game identifier
        player_id: The player to investigate
        
    Returns:
        An investigation prompt string
    """
    try:
        profile = db.get_player_profile(player_id)
        if not profile:
            return f"Player {player_id} not found in game {game_id}."
        
        history = db.get_game_history(game_id=game_id, speaker=player_id, limit=20)
        relations = knowledge_graph.get_player_relations(player_id)
        
        prompt = f"""# Player Investigation: {player_id}

## Player Profile:
- **Suspicion Score**: {profile.get('suspicion_score', 0.0):.2f}
- **Assumed Role**: {profile.get('role_assumed', 'Unknown')}
- **Personality**: {profile.get('personality', 'Unknown')}

## Historical Actions ({len(history)} records):
"""
        if history:
            for event in history[-10:]:
                prompt += f"- **Round {event['round_num']}** ({event['action_type']}): {event['content'][:150]}\n"
        else:
            prompt += "- No history found\n"
        
        prompt += f"\n## Relationship Network:\n"
        if relations.get("outgoing"):
            prompt += f"**Outgoing Relations**: {len(relations['outgoing'])}\n"
            for rel in relations['outgoing'][:5]:
                prompt += f"  - {rel.get('type', 'unknown')} (weight: {rel.get('weight', 0)})\n"
        
        if relations.get("incoming"):
            prompt += f"**Incoming Relations**: {len(relations['incoming'])}\n"
            for rel in relations['incoming'][:5]:
                prompt += f"  - {rel.get('type', 'unknown')} (weight: {rel.get('weight', 0)})\n"
        
        centrality = knowledge_graph.calculate_centrality(player_id)
        prompt += f"\n**Network Centrality**: {centrality:.2f}\n"
        
        prompt += f"""
## Investigation Steps:
1. Review full history: Use `recall_memory` with player_id="{player_id}"
2. Check relationships: Use `get_player_relations` with player_id="{player_id}"
3. Analyze contradictions: Look for conflicting statements in history
4. Check for patterns: Use `detect_wolf_patterns` to see if {player_id} appears in suspicious pairs
5. Update suspicion: Use `analyze_suspicion` if you find new evidence

## Key Questions:
- Does {player_id} have consistent statements?
- Who does {player_id} attack/support?
- Is {player_id} part of a suspicious pair?
- What is {player_id}'s voting pattern?
"""
        
        return prompt
    except Exception as e:
        logger.error(f"Error generating investigation prompt: {e}")
        return f"Error generating investigation: {str(e)}"


@YA_MCPServer_Prompt(
    name="game_strategy_guide",
    title="Game Strategy Guide",
    description="Generate a comprehensive strategy guide based on current game state and role"
)
async def game_strategy_guide_prompt(
    game_id: str,
    current_role: str
) -> str:
    """
    Generate a strategy guide prompt.
    
    Args:
        game_id: The game identifier
        current_role: Current role of the player
        
    Returns:
        A strategy guide prompt string
    """
    try:
        game_state = db.get_game_state(game_id)
        if not game_state:
            return f"Game {game_id} not found."
        
        alive_players = game_state.get("alive_players", [])
        current_round = game_state.get("current_round", 1)
        alive_count = len(alive_players)
        
        profiles = db.get_all_player_profiles(game_id=game_id)
        high_suspicion = [
            p["player_id"] for p in profiles
            if p.get("suspicion_score", 0.0) > 0.7 and p["player_id"] in alive_players
        ]
        
        prompt = f"""# Game Strategy Guide - {current_role.upper()}

## Current Game State:
- **Round**: {current_round}
- **Alive Players**: {alive_count} ({', '.join(alive_players)})
- **High Suspicion Players**: {', '.join(high_suspicion) if high_suspicion else 'None'}

## Role-Specific Strategy:

### As {current_role}:
"""
        
        if current_role == "seer":
            prompt += f"""
1. **Night Phase (Checking)**:
   - Use `calculate_action_utility` to decide who to check
   - Prioritize players with medium-high suspicion (0.5-0.8)
   - Avoid checking obvious villagers (suspicion < 0.3)
   - Consider checking players who are being defended

2. **Day Phase (Revealing)**:
   - Reveal your identity strategically
   - Share check results to guide voting
   - Use `record_event` to document your checks

3. **Key Tools**:
   - `calculate_action_utility`: Decide who to check
   - `analyze_suspicion`: Update suspicion after checks
   - `get_player_relations`: Find suspicious pairs
"""
        elif current_role == "villager":
            prompt += f"""
1. **Observation Phase**:
   - Use `recall_memory` to review all player statements
   - Use `get_player_relations` to find attack/support patterns
   - Look for contradictions with `analyze_suspicion`

2. **Voting Phase**:
   - Use `calculate_action_utility` to decide who to vote
   - Focus on players with high suspicion scores
   - Consider voting patterns and relationships

3. **Key Tools**:
   - `recall_memory`: Review player statements
   - `detect_wolf_patterns`: Find suspicious pairs
   - `calculate_action_utility`: Make voting decisions
"""
        else:
            prompt += f"""
1. **General Strategy**:
   - Use `query_game_state` to stay updated
   - Use `recall_memory` to review history
   - Use `analyze_suspicion` to track threats
   - Use `calculate_action_utility` for decisions
"""
        
        prompt += f"""
## Critical Game Phases:

### Early Game (Rounds 1-2):
- Build knowledge graph with `record_event`
- Identify initial suspects with `analyze_suspicion`
- Use `get_player_relations` to map relationships

### Mid Game (Rounds 3-4):
- Use `detect_wolf_patterns` to find suspicious pairs
- Review key statements with `recall_memory`
- Update suspicion scores based on new evidence

### Late Game (Rounds 5+):
- Use `calculate_action_utility` for critical decisions
- Focus on remaining high-suspicion players
- Consider game state (alive count) in decisions

## Recommended Tool Sequence:
1. `query_game_state` - Get current status
2. `recall_memory` - Review recent events
3. `analyze_suspicion` - Update suspicion scores
4. `get_player_relations` - Analyze relationships
5. `detect_wolf_patterns` - Find patterns
6. `calculate_action_utility` - Make decision
7. `record_event` - Record your action
"""
        
        return prompt
    except Exception as e:
        logger.error(f"Error generating strategy guide: {e}")
        return f"Error generating strategy guide: {str(e)}"
