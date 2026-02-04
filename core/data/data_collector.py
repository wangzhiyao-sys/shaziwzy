import sqlite3
from typing import List, Dict, Any, Optional

class TrainingDataCollector:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def fetch_game_history(self, game_id: str) -> List[Dict[str, Any]]:
        """
        Fetches game history for a specific game.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM GameHistory WHERE game_id = ?", (game_id,))
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def extract_features_and_labels(self, game_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts features and labels from game history.
        This is a placeholder for actual feature engineering.
        """
        # Example: simple feature extraction
        training_samples = []
        for event in game_history:
            if event.get('action_type') == 'speak':
                sample = {
                    'feature_vector': self._text_to_vector(event['content']),
                    'label': self._determine_label(event), # Placeholder for labeling logic
                    'game_id': event['game_id'],
                    'player_id': event['speaker']
                }
                training_samples.append(sample)
        return training_samples

    def _text_to_vector(self, text: str) -> List[float]:
        """
        Converts text to a simple vector representation.
        Placeholder for a real embedding model.
        """
        return [float(ord(c)) for c in text]

    def _determine_label(self, event: Dict[str, Any]) -> int:
        """
        Determines a label for a given event.
        Placeholder for actual labeling logic.
        """
        # Example: 1 if 'suspicious' in content, else 0
        return 1 if 'suspicious' in event.get('content', '').lower() else 0

    def collect_and_store_data(self, game_id: str):
        """
        Main method to fetch history, extract features/labels, and store them.
        """
        history = self.fetch_game_history(game_id)
        training_data = self.extract_features_and_labels(history)
        
        with self._connect() as conn:
            cursor = conn.cursor()
            for sample in training_data:
                cursor.execute(
                    """
                    INSERT INTO TrainingData (game_id, player_id, features, label)
                    VALUES (?, ?, ?, ?)
                    """,
                    (sample['game_id'], sample['player_id'], str(sample['feature_vector']), sample['label'])
                )
            conn.commit()

if __name__ == '__main__':
    # Example usage
    collector = TrainingDataCollector(db_path='../../data/game.db')
    # Assuming game 'game_001' exists and has history
    # collector.collect_and_store_data('game_001') 
    print("Data collector module created.")
