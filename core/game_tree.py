from typing import List, Dict, Optional, Tuple
from enum import Enum
from modules.YA_Common.utils.logger import get_logger

logger = get_logger("game_tree")


class ActionType(Enum):
    CHECK = "check"
    VOTE = "vote"
    SPEAK = "speak"


class GameTreeSearch:
    def __init__(self):
        self.alive_players: List[str] = []
        self.suspicion_scores: Dict[str, float] = {}
        self.player_roles: Dict[str, str] = {}
    
    def calculate_action_utility(
        self,
        action_candidates: List[Dict],
        current_role: str,
        alive_count: int,
        suspicion_scores: Dict[str, float]
    ) -> List[Dict]:
        self.alive_players = list(suspicion_scores.keys())
        self.suspicion_scores = suspicion_scores
        
        utilities = []
        
        for action in action_candidates:
            action_type = action.get("type")
            target = action.get("target")
            
            if action_type == ActionType.CHECK.value:
                utility = self._calculate_check_utility(target, alive_count)
            elif action_type == ActionType.VOTE.value:
                utility = self._calculate_vote_utility(target, alive_count)
            else:
                utility = 0.5
            
            utilities.append({
                **action,
                "utility": utility,
                "recommendation": self._get_recommendation(utility)
            })
        
        utilities.sort(key=lambda x: x["utility"], reverse=True)
        logger.debug(f"Calculated utilities for {len(utilities)} actions")
        return utilities
    
    def _calculate_check_utility(
        self,
        target: str,
        alive_count: int
    ) -> float:
        if target not in self.suspicion_scores:
            return 0.3
        
        suspicion = self.suspicion_scores[target]
        
        information_gain = suspicion * 0.6
        
        strategic_value = 0.0
        if suspicion > 0.7:
            strategic_value = 0.3
        elif suspicion < 0.3:
            strategic_value = 0.2
        
        urgency_factor = 1.0 / max(alive_count, 1)
        
        utility = information_gain + strategic_value + urgency_factor * 0.1
        return min(1.0, utility)
    
    def _calculate_vote_utility(
        self,
        target: str,
        alive_count: int
    ) -> float:
        if target not in self.suspicion_scores:
            return 0.3
        
        suspicion = self.suspicion_scores[target]
        
        elimination_value = suspicion * 0.7
        
        risk_factor = 0.0
        if alive_count <= 3:
            risk_factor = 0.2
        
        consensus_factor = 0.1
        
        utility = elimination_value + risk_factor + consensus_factor
        return min(1.0, utility)
    
    def _get_recommendation(self, utility: float) -> str:
        if utility >= 0.8:
            return "highly_recommended"
        elif utility >= 0.6:
            return "recommended"
        elif utility >= 0.4:
            return "neutral"
        else:
            return "not_recommended"
    
    def minimax_decision(
        self,
        current_state: Dict,
        depth: int = 2,
        is_maximizing: bool = True
    ) -> Tuple[str, float]:
        if depth == 0:
            return None, self._evaluate_state(current_state)
        
        best_action = None
        best_value = float("-inf") if is_maximizing else float("inf")
        
        actions = self._generate_actions(current_state)
        
        for action in actions:
            new_state = self._apply_action(current_state, action)
            _, value = self.minimax_decision(new_state, depth - 1, not is_maximizing)
            
            if is_maximizing:
                if value > best_value:
                    best_value = value
                    best_action = action
            else:
                if value < best_value:
                    best_value = value
                    best_action = action
        
        return best_action, best_value
    
    def _evaluate_state(self, state: Dict) -> float:
        alive_wolves = state.get("alive_wolves", 0)
        alive_villagers = state.get("alive_villagers", 0)
        
        if alive_wolves == 0:
            return 1.0
        if alive_villagers == 0:
            return -1.0
        
        ratio = alive_villagers / (alive_wolves + alive_villagers)
        return ratio
    
    def _generate_actions(self, state: Dict) -> List[Dict]:
        actions = []
        alive_players = state.get("alive_players", [])
        
        for player in alive_players:
            if state.get("can_check"):
                actions.append({"type": "check", "target": player})
            if state.get("can_vote"):
                actions.append({"type": "vote", "target": player})
        
        return actions
    
    def _apply_action(self, state: Dict, action: Dict) -> Dict:
        new_state = state.copy()
        action_type = action.get("type")
        target = action.get("target")
        
        if action_type == "check":
            new_state["checked_players"] = new_state.get("checked_players", []) + [target]
        elif action_type == "vote":
            new_state["voted_players"] = new_state.get("voted_players", []) + [target]
        
        return new_state
    
    def reset(self):
        self.alive_players.clear()
        self.suspicion_scores.clear()
        self.player_roles.clear()
        logger.info("Game tree search reset")
