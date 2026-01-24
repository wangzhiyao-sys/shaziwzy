from typing import Dict, List, Optional, Any
from tools import YA_MCPServer_Tool
from core.database import GameDatabase
from core.bayesian_inference import BayesianInference
from core.knowledge_graph import KnowledgeGraph
from core.game_tree import GameTreeSearch
from modules.YA_Common.utils.logger import get_logger

logger = get_logger("game_tools")

db = GameDatabase()
bayesian = BayesianInference()
knowledge_graph = KnowledgeGraph()
game_tree = GameTreeSearch()


@YA_MCPServer_Tool(
    name="query_game_state",
    title="Query Game State",
    description="Get current game state including alive players, current round, and game status"
)
async def query_game_state(game_id: str) -> Dict[str, Any]:
    """Query the current game state.
    
    Args:
        game_id: The unique identifier for the game session
        
    Returns:
        Dict containing game state information:
        - current_round: Current round number
        - alive_players: List of alive player IDs
        - game_status: Current game status
    """
    try:
        game_state = db.get_game_state(game_id)
        
        if not game_state:
            return {
                "error": "Game not found",
                "game_id": game_id
            }
        
        logger.info(f"Queried game state for game_id: {game_id}")
        
        return {
            "game_id": game_id,
            "current_round": game_state.get("current_round", 1),
            "alive_players": game_state.get("alive_players", []),
            "game_status": game_state.get("game_status", "active")
        }
    except Exception as e:
        logger.error(f"Error querying game state: {e}")
        return {"error": str(e)}


@YA_MCPServer_Tool(
    name="recall_memory",
    title="Recall Memory",
    description="Retrieve historical statements and actions from a specific player using RAG algorithm"
)
async def recall_memory(
    player_id: str,
    game_id: Optional[str] = None,
    round_num: Optional[int] = None,
    action_type: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """Recall memory of a player's past statements and actions.
    
    Args:
        player_id: The player ID to retrieve memory for
        game_id: Optional game ID to filter by
        round_num: Optional round number to filter by
        action_type: Optional action type filter (e.g., 'speak', 'vote', 'check')
        limit: Maximum number of records to return
        
    Returns:
        Dict containing:
        - player_id: The queried player ID
        - memories: List of historical records
        - summary: Summary of player behavior
    """
    try:
        history = db.get_game_history(
            game_id=game_id,
            round_num=round_num,
            speaker=player_id,
            action_type=action_type,
            limit=limit
        )
        
        memories = []
        for record in history:
            memories.append({
                "round": record["round_num"],
                "content": record["content"],
                "action_type": record["action_type"],
                "timestamp": record["timestamp"]
            })
        
        summary = _generate_memory_summary(memories)
        
        logger.info(f"Recalled {len(memories)} memories for player: {player_id}")
        
        return {
            "player_id": player_id,
            "memories": memories,
            "summary": summary,
            "count": len(memories)
        }
    except Exception as e:
        logger.error(f"Error recalling memory: {e}")
        return {"error": str(e)}


def _generate_memory_summary(memories: List[Dict]) -> str:
    if not memories:
        return "No historical records found"
    
    action_types = {}
    for mem in memories:
        action_type = mem.get("action_type", "unknown")
        action_types[action_type] = action_types.get(action_type, 0) + 1
    
    summary_parts = [f"Total records: {len(memories)}"]
    for action_type, count in action_types.items():
        summary_parts.append(f"{action_type}: {count}")
    
    return "; ".join(summary_parts)


@YA_MCPServer_Tool(
    name="analyze_suspicion",
    title="Analyze Suspicion",
    description="Analyze player suspicion using Bayesian inference algorithm based on evidence"
)
async def analyze_suspicion(
    player_id: str,
    evidence_score: float,
    evidence_type: str = "general",
    description: str = "",
    game_id: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze and update suspicion score for a player using Bayesian inference.
    
    Args:
        player_id: The player ID to analyze
        evidence_score: Evidence score (0.0-1.0, higher means more suspicious)
        evidence_type: Type of evidence (e.g., 'contradiction', 'behavior', 'vote_pattern')
        description: Description of the evidence
        game_id: Optional game ID
        
    Returns:
        Dict containing:
        - player_id: The analyzed player ID
        - previous_suspicion: Previous suspicion score
        - current_suspicion: Updated suspicion score
        - evidence_count: Number of evidence pieces collected
    """
    try:
        previous_suspicion = bayesian.get_suspicion(player_id)
        
        current_suspicion = bayesian.update_suspicion(
            player_id=player_id,
            evidence_score=evidence_score,
            evidence_type=evidence_type,
            description=description
        )
        
        db.update_player_profile(
            player_id=player_id,
            suspicion_score=current_suspicion,
            game_id=game_id
        )
        
        evidence_count = len(bayesian.evidence_history.get(player_id, []))
        
        logger.info(
            f"Analyzed suspicion for {player_id}: "
            f"{previous_suspicion:.3f} -> {current_suspicion:.3f}"
        )
        
        return {
            "player_id": player_id,
            "previous_suspicion": round(previous_suspicion, 3),
            "current_suspicion": round(current_suspicion, 3),
            "evidence_count": evidence_count,
            "evidence_type": evidence_type
        }
    except Exception as e:
        logger.error(f"Error analyzing suspicion: {e}")
        return {"error": str(e)}


@YA_MCPServer_Tool(
    name="record_event",
    title="Record Event",
    description="Record a game event to the database and update knowledge graph"
)
async def record_event(
    round_num: int,
    speaker: str,
    content: str,
    action_type: str,
    game_id: Optional[str] = None,
    target_player: Optional[str] = None,
    relation_type: Optional[str] = None
) -> Dict[str, Any]:
    """Record a game event to the database.
    
    Args:
        round_num: Round number when the event occurred
        speaker: Player ID who performed the action
        content: Content of the action (e.g., speech text)
        action_type: Type of action (e.g., 'speak', 'vote', 'check')
        game_id: Optional game ID
        target_player: Optional target player ID (for vote, check, etc.)
        relation_type: Optional relation type for knowledge graph (e.g., 'attack', 'support')
        
    Returns:
        Dict containing:
        - success: Whether the event was recorded
        - event_id: Record ID
        - timestamp: When the event was recorded
    """
    try:
        db.record_event(
            round_num=round_num,
            speaker=speaker,
            content=content,
            action_type=action_type,
            game_id=game_id
        )
        
        if target_player and relation_type:
            knowledge_graph.add_edge(
                source=speaker,
                target=target_player,
                relation_type=relation_type,
                weight=1.0,
                metadata={
                    "round": round_num,
                    "action_type": action_type,
                    "content": content
                }
            )
        
        knowledge_graph.add_node(speaker)
        if target_player:
            knowledge_graph.add_node(target_player)
        
        logger.info(
            f"Recorded event: {action_type} by {speaker} "
            f"in round {round_num}"
        )
        
        return {
            "success": True,
            "round_num": round_num,
            "speaker": speaker,
            "action_type": action_type,
            "game_id": game_id
        }
    except Exception as e:
        logger.error(f"Error recording event: {e}")
        return {"success": False, "error": str(e)}


@YA_MCPServer_Tool(
    name="get_player_relations",
    title="Get Player Relations",
    description="Get relationship network for a player using knowledge graph"
)
async def get_player_relations(player_id: str) -> Dict[str, Any]:
    """Get relationship network for a player.
    
    Args:
        player_id: The player ID to analyze
        
    Returns:
        Dict containing:
        - player_id: The queried player ID
        - relations: Incoming and outgoing relations
        - centrality: Centrality score in the network
    """
    try:
        relations = knowledge_graph.get_player_relations(player_id)
        centrality = knowledge_graph.calculate_centrality(player_id)
        
        logger.info(f"Retrieved relations for player: {player_id}")
        
        return {
            "player_id": player_id,
            "relations": relations,
            "centrality": round(centrality, 3)
        }
    except Exception as e:
        logger.error(f"Error getting player relations: {e}")
        return {"error": str(e)}


@YA_MCPServer_Tool(
    name="calculate_action_utility",
    title="Calculate Action Utility",
    description="Calculate utility scores for possible actions using game tree search"
)
async def calculate_action_utility(
    action_candidates: List[Dict],
    current_role: str,
    alive_count: int,
    suspicion_scores: Dict[str, float]
) -> Dict[str, Any]:
    """Calculate utility scores for possible actions.
    
    Args:
        action_candidates: List of action dictionaries with 'type' and 'target' keys
        current_role: Current role of the player (e.g., 'seer', 'villager')
        alive_count: Number of alive players
        suspicion_scores: Dictionary mapping player_id to suspicion score
        
    Returns:
        Dict containing:
        - actions: List of actions with utility scores and recommendations
        - best_action: The action with highest utility
    """
    try:
        utilities = game_tree.calculate_action_utility(
            action_candidates=action_candidates,
            current_role=current_role,
            alive_count=alive_count,
            suspicion_scores=suspicion_scores
        )
        
        best_action = utilities[0] if utilities else None
        
        logger.info(f"Calculated utilities for {len(utilities)} actions")
        
        return {
            "actions": utilities,
            "best_action": best_action,
            "count": len(utilities)
        }
    except Exception as e:
        logger.error(f"Error calculating action utility: {e}")
        return {"error": str(e)}


@YA_MCPServer_Tool(
    name="detect_wolf_patterns",
    title="Detect Wolf Patterns",
    description="Detect suspicious patterns like wolf pairs or collusion using knowledge graph"
)
async def detect_wolf_patterns(threshold: float = 0.7) -> Dict[str, Any]:
    """Detect suspicious patterns in player relationships.
    
    Args:
        threshold: Threshold for detecting suspicious pairs (0.0-1.0)
        
    Returns:
        Dict containing:
        - suspicious_pairs: List of suspicious player pairs
        - collusion_scores: Collusion scores for each player
        - attack_network: Network of attack relationships
    """
    try:
        suspicious_pairs = knowledge_graph.detect_wolf_pair(threshold=threshold)
        
        all_players = list(knowledge_graph.nodes)
        collusion_scores = knowledge_graph.detect_collusion(all_players)
        
        attack_network = knowledge_graph.get_attack_network()
        
        logger.info(f"Detected {len(suspicious_pairs)} suspicious pairs")
        
        return {
            "suspicious_pairs": suspicious_pairs,
            "collusion_scores": collusion_scores,
            "attack_network": attack_network
        }
    except Exception as e:
        logger.error(f"Error detecting wolf patterns: {e}")
        return {"error": str(e)}
