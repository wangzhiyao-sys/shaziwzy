from typing import Dict, List, Optional, Any
from tools import YA_MCPServer_Tool
from core.database import GameDatabase
from core.bayesian_inference import BayesianInference
from core.knowledge_graph import KnowledgeGraph
from modules.YA_Common.utils.logger import get_logger

logger = get_logger("game_init")

db = GameDatabase()
bayesian = BayesianInference()
knowledge_graph = KnowledgeGraph()


@YA_MCPServer_Tool(
    name="initialize_game",
    title="Initialize Game",
    description="Initialize a new game session with players and roles"
)
async def initialize_game(
    game_id: str,
    player_ids: List[str],
    total_wolves: int = 2
) -> Dict[str, Any]:
    """Initialize a new game session.
    
    Args:
        game_id: Unique identifier for the game session
        player_ids: List of player IDs participating in the game
        total_wolves: Number of wolves in the game (default: 2)
        
    Returns:
        Dict containing:
        - game_id: The game ID
        - players: List of initialized players
        - status: Initialization status
    """
    try:
        db.update_game_state(
            game_id=game_id,
            current_round=1,
            alive_players=player_ids,
            game_status="active"
        )
        
        bayesian.initialize_priors(player_ids, total_wolves)
        
        for player_id in player_ids:
            db.update_player_profile(
                player_id=player_id,
                suspicion_score=bayesian.get_suspicion(player_id),
                game_id=game_id
            )
            knowledge_graph.add_node(player_id)
        
        logger.info(f"Initialized game {game_id} with {len(player_ids)} players")
        
        return {
            "game_id": game_id,
            "players": player_ids,
            "total_wolves": total_wolves,
            "status": "initialized",
            "current_round": 1
        }
    except Exception as e:
        logger.error(f"Error initializing game: {e}")
        return {"error": str(e)}


@YA_MCPServer_Tool(
    name="reset_game",
    title="Reset Game",
    description="Reset all game data and algorithms for a new game"
)
async def reset_game(game_id: Optional[str] = None) -> Dict[str, Any]:
    """Reset game data and algorithms.
    
    Args:
        game_id: Optional game ID to reset specific game
        
    Returns:
        Dict containing reset status
    """
    try:
        bayesian.reset()
        knowledge_graph.reset()
        
        logger.info(f"Reset game data for game_id: {game_id}")
        
        return {
            "status": "reset",
            "game_id": game_id
        }
    except Exception as e:
        logger.error(f"Error resetting game: {e}")
        return {"error": str(e)}
