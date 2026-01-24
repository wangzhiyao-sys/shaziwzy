import os
import json
from resources import YA_MCPServer_Resource
from typing import Any
from core.database import GameDatabase
from modules.YA_Common.utils.logger import get_logger

logger = get_logger("game_resources")

db = GameDatabase()


@YA_MCPServer_Resource(
    "game://game_state/{game_id}",
    name="game_state_resource",
    title="Game State Resource",
    description="Get current game state including alive players, round number, and game status"
)
def get_game_state_resource(game_id: str) -> Any:
    """
    Get current game state as a resource.
    
    Args:
        game_id: The game identifier
        
    Returns:
        JSON string containing game state information
    """
    try:
        game_state = db.get_game_state(game_id)
        if not game_state:
            return json.dumps({"error": "Game not found", "game_id": game_id}, ensure_ascii=False)
        
        result = {
            "game_id": game_id,
            "current_round": game_state.get("current_round", 1),
            "alive_players": game_state.get("alive_players", []),
            "game_status": game_state.get("game_status", "unknown"),
            "updated_at": game_state.get("updated_at", "")
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error getting game state resource: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@YA_MCPServer_Resource(
    "game://player_profile/{player_id}",
    name="player_profile_resource",
    title="Player Profile Resource",
    description="Get player profile including suspicion score, assumed role, and personality"
)
def get_player_profile_resource(player_id: str) -> Any:
    """
    Get player profile as a resource.
    
    Args:
        player_id: The player identifier
        
    Returns:
        JSON string containing player profile information
    """
    try:
        profile = db.get_player_profile(player_id)
        if not profile:
            return json.dumps({"error": "Player not found", "player_id": player_id}, ensure_ascii=False)
        
        result = {
            "player_id": profile.get("player_id"),
            "role_assumed": profile.get("role_assumed"),
            "suspicion_score": profile.get("suspicion_score", 0.0),
            "personality": profile.get("personality"),
            "game_id": profile.get("game_id"),
            "updated_at": profile.get("updated_at", "")
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error getting player profile resource: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@YA_MCPServer_Resource(
    "game://game_history/{game_id}",
    name="game_history_resource",
    title="Game History Resource",
    description="Get game history for a specific game (last 50 records). Use the recall_memory tool for filtered queries."
)
def get_game_history_resource(game_id: str) -> Any:
    """
    Get game history as a resource.
    
    Args:
        game_id: The game identifier
        
    Returns:
        JSON string containing game history (last 50 records)
    """
    try:
        history = db.get_game_history(
            game_id=game_id,
            limit=50
        )
        
        result = {
            "game_id": game_id,
            "round_num": round_num,
            "count": len(history),
            "history": [
                {
                    "id": record.get("id"),
                    "round_num": record.get("round_num"),
                    "speaker": record.get("speaker"),
                    "content": record.get("content"),
                    "action_type": record.get("action_type"),
                    "timestamp": record.get("timestamp")
                }
                for record in history
            ]
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error getting game history resource: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@YA_MCPServer_Resource(
    "file:///docs/GAME_USAGE.md",
    name="game_usage_guide",
    title="Game Usage Guide",
    description="Complete usage guide for MCP-PolyGame-Agent with examples and API documentation"
)
def get_game_usage_guide() -> Any:
    """
    Get the game usage guide documentation.
    
    Returns:
        Content of the game usage guide
    """
    try:
        with open("docs/GAME_USAGE.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Game usage guide not found. Please check docs/GAME_USAGE.md"


@YA_MCPServer_Resource(
    "file:///docs/QUICK_START.md",
    name="quick_start_guide",
    title="Quick Start Guide",
    description="Quick start guide with step-by-step instructions for using MCP-PolyGame-Agent"
)
def get_quick_start_guide() -> Any:
    """
    Get the quick start guide.
    
    Returns:
        Content of the quick start guide
    """
    try:
        with open("docs/QUICK_START.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Quick start guide not found. Please check docs/QUICK_START.md"
