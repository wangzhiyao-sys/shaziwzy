from typing import Dict, List, Optional
from modules.YA_Common.utils.logger import get_logger

logger = get_logger("bayesian_inference")


class BayesianInference:
    def __init__(self):
        self.prior_probabilities: Dict[str, float] = {}
        self.evidence_history: Dict[str, List[Dict]] = {}
        
    def initialize_priors(self, player_ids: List[str], total_wolves: int = 2):
        total_players = len(player_ids)
        wolf_prior = total_wolves / total_players
        villager_prior = 1.0 - wolf_prior
        
        for player_id in player_ids:
            self.prior_probabilities[player_id] = wolf_prior
            self.evidence_history[player_id] = []
        
        logger.info(f"Initialized priors for {len(player_ids)} players")
    
    def update_suspicion(
        self,
        player_id: str,
        evidence_score: float,
        evidence_type: str = "general",
        description: str = ""
    ) -> float:
        if player_id not in self.prior_probabilities:
            self.prior_probabilities[player_id] = 0.4
        
        prior = self.prior_probabilities[player_id]
        
        evidence_history = self.evidence_history.get(player_id, [])
        evidence_history.append({
            "score": evidence_score,
            "type": evidence_type,
            "description": description
        })
        self.evidence_history[player_id] = evidence_history
        
        likelihood_wolf = self._calculate_likelihood(evidence_score, is_wolf=True)
        likelihood_villager = self._calculate_likelihood(evidence_score, is_wolf=False)
        
        posterior = (likelihood_wolf * prior) / (
            likelihood_wolf * prior + likelihood_villager * (1 - prior)
        )
        
        self.prior_probabilities[player_id] = posterior
        
        logger.debug(
            f"Updated suspicion for {player_id}: {prior:.3f} -> {posterior:.3f} "
            f"(evidence: {evidence_score:.3f})"
        )
        
        return posterior
    
    def _calculate_likelihood(self, evidence_score: float, is_wolf: bool) -> float:
        if is_wolf:
            return 0.5 + 0.5 * evidence_score
        else:
            return 0.5 + 0.5 * (1 - evidence_score)
    
    def get_suspicion(self, player_id: str) -> float:
        return self.prior_probabilities.get(player_id, 0.4)
    
    def get_all_suspicions(self) -> Dict[str, float]:
        return self.prior_probabilities.copy()
    
    def analyze_contradiction(
        self,
        player_id: str,
        current_statement: str,
        historical_statements: List[Dict]
    ) -> float:
        if not historical_statements:
            return 0.0
        
        contradiction_score = 0.0
        contradiction_count = 0
        
        for hist in historical_statements:
            if self._detect_contradiction(current_statement, hist.get("content", "")):
                contradiction_count += 1
                contradiction_score += 0.3
        
        if contradiction_count > 0:
            final_score = min(0.9, contradiction_score / len(historical_statements))
            return final_score
        
        return 0.0
    
    def _detect_contradiction(self, statement1: str, statement2: str) -> bool:
        statement1_lower = statement1.lower()
        statement2_lower = statement2.lower()
        
        contradiction_keywords = [
            ("not", "is"),
            ("never", "always"),
            ("did", "didn't"),
            ("was", "wasn't"),
            ("saw", "didn't see"),
        ]
        
        for neg, pos in contradiction_keywords:
            if (neg in statement1_lower and pos in statement2_lower) or \
               (neg in statement2_lower and pos in statement1_lower):
                return True
        
        return False
    
    def reset(self):
        self.prior_probabilities.clear()
        self.evidence_history.clear()
        logger.info("Bayesian inference model reset")
