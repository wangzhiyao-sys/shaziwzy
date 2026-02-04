from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
from modules.YA_Common.utils.logger import get_logger

logger = get_logger("knowledge_graph")


class KnowledgeGraph:
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[Tuple[str, str], Dict] = {}
        self.node_attributes: Dict[str, Dict] = {}
    
    def add_node(self, player_id: str, attributes: Optional[Dict] = None):
        self.nodes.add(player_id)
        if attributes:
            self.node_attributes[player_id] = attributes
        logger.debug(f"Added node: {player_id}")
    
    def add_edge(
        self,
        source: str,
        target: str,
        relation_type: str,
        weight: float = 1.0,
        metadata: Optional[Dict] = None
    ):
        if source not in self.nodes:
            self.add_node(source)
        if target not in self.nodes:
            self.add_node(target)
        
        edge_key = (source, target)
        if edge_key not in self.edges:
            self.edges[edge_key] = {
                "relations": [],
                "total_weight": 0.0
            }
        
        relation = {
            "type": relation_type,
            "weight": weight,
            "metadata": metadata or {}
        }
        self.edges[edge_key]["relations"].append(relation)
        self.edges[edge_key]["total_weight"] += weight
        
        logger.debug(f"Added edge: {source} -> {target} ({relation_type})")
    
    def get_player_relations(self, player_id: str) -> Dict[str, List[Dict]]:
        relations = defaultdict(list)
        
        for (source, target), edge_data in self.edges.items():
            if source == player_id:
                relations["outgoing"].extend(edge_data["relations"])
            if target == player_id:
                relations["incoming"].extend(edge_data["relations"])
        
        return dict(relations)
    
    def detect_wolf_pair(self, threshold: float = 0.7) -> List[Tuple[str, str]]:
        suspicious_pairs = []
        
        for (source, target), edge_data in self.edges.items():
            support_count = 0
            attack_count = 0
            
            for relation in edge_data["relations"]:
                if relation["type"] == "support":
                    support_count += relation["weight"]
                elif relation["type"] == "attack":
                    attack_count += relation["weight"]
            
            if support_count > 0 and attack_count == 0:
                support_ratio = support_count / edge_data["total_weight"]
                if support_ratio >= threshold:
                    suspicious_pairs.append((source, target))
        
        logger.debug(f"Detected {len(suspicious_pairs)} suspicious pairs")
        return suspicious_pairs
    
    def detect_collusion(self, player_ids: List[str]) -> Dict[str, float]:
        collusion_scores = {}
        
        for player_id in player_ids:
            relations = self.get_player_relations(player_id)
            outgoing = relations.get("outgoing", [])
            
            support_weight = sum(
                r["weight"] for r in outgoing if r["type"] == "support"
            )
            total_weight = sum(r["weight"] for r in outgoing)
            
            if total_weight > 0:
                collusion_score = support_weight / total_weight
                collusion_scores[player_id] = collusion_score
        
        return collusion_scores
    
    def get_attack_network(self) -> Dict[str, List[str]]:
        attack_network = defaultdict(list)
        
        for (source, target), edge_data in self.edges.items():
            for relation in edge_data["relations"]:
                if relation["type"] == "attack":
                    attack_network[source].append(target)
        
        return dict(attack_network)
    
    def get_support_network(self) -> Dict[str, List[str]]:
        support_network = defaultdict(list)
        
        for (source, target), edge_data in self.edges.items():
            for relation in edge_data["relations"]:
                if relation["type"] == "support":
                    support_network[source].append(target)
        
        return dict(support_network)
    
    def calculate_centrality(self, player_id: str) -> float:
        incoming_count = sum(
            1 for (_, target) in self.edges.keys() if target == player_id
        )
        outgoing_count = sum(
            1 for (source, _) in self.edges.keys() if source == player_id
        )
        
        total_edges = len(self.edges)
        if total_edges == 0:
            return 0.0
        
        centrality = (incoming_count + outgoing_count) / total_edges
        return centrality
    
    def reset(self):
        self.nodes.clear()
        self.edges.clear()
        self.node_attributes.clear()
        logger.info("Knowledge graph reset")
