import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from modules.YA_Common.utils.logger import get_logger

class TrainingDataCollector:
    """
    Collects, processes, and stores training data from game histories.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = get_logger("DataCollector")
        # Initialize a TF-IDF Vectorizer for text processing
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.logger.info("TrainingDataCollector initialized.")

    def _connect(self):
        """Establishes a connection to the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            self.logger.error(f"Database connection error: {e}")
            return None

    def fetch_game_history(self, game_id: str) -> List[Dict[str, Any]]:
        """
        Fetches all game events for a specific game.
        """
        self.logger.info(f"Fetching game history for game_id: {game_id}")
        conn = self._connect()
        if not conn:
            return []
        try:
            with conn:
                cursor = conn.cursor()
                # The 'content' column may contain JSON strings for actions like 'vote'
                cursor.execute("SELECT round_num, speaker, content, action_type FROM GameHistory WHERE game_id = ? ORDER BY round_num", (game_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Failed to fetch game history for {game_id}: {e}")
            return []

    def fetch_player_roles(self, game_id: str) -> Dict[str, str]:
        """
        Fetches the ground truth roles of players for a given game.
        This assumes roles are stored in PlayerProfile after the game ends.
        """
        self.logger.info(f"Fetching player roles for game_id: {game_id}")
        conn = self._connect()
        if not conn:
            return {}
        try:
            with conn:
                cursor = conn.cursor()
                # Assuming 'role_assumed' stores the true role for labeling purposes
                cursor.execute("SELECT player_id, role_assumed FROM PlayerProfile WHERE game_id = ?", (game_id,))
                rows = cursor.fetchall()
                roles = {row['player_id']: row['role_assumed'] for row in rows}
                if not roles:
                    self.logger.warning(f"No player roles found for game_id: {game_id}. Labeling will be incomplete.")
                return roles
        except sqlite3.Error as e:
            self.logger.error(f"Failed to fetch player roles for {game_id}: {e}")
            return {}

    def extract_features_and_labels(self, game_history: List[Dict[str, Any]], player_roles: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Extracts structured features and determines labels from game history.
        """
        self.logger.info(f"Extracting features and labels from {len(game_history)} events.")
        if not game_history:
            return []

        # Fit the vectorizer on all speech content first
        all_speech = [event['content'] for event in game_history if event['action_type'] == 'speak']
        if all_speech:
            self.vectorizer.fit(all_speech)

        training_samples = []
        for event in game_history:
            speaker_id = event['speaker']
            speaker_role = player_roles.get(speaker_id)
            if not speaker_role:
                continue # Skip if we don't know the role of the speaker

            features = {
                'round_num': event['round_num'],
                'speaker_role': speaker_role, # Ground truth role for context
            }
            
            action_type = event['action_type']
            content = event['content']
            target_player = None

            # Process content based on action type
            if action_type == 'speak':
                text_vector = self.vectorizer.transform([content]).toarray().flatten().tolist()
                features['text_vector'] = text_vector
            elif action_type in ['vote', 'kill', 'check']:
                try:
                    # Content for actions is expected to be a JSON string like '{"target": "player2"}'
                    action_details = json.loads(content)
                    target_player = action_details.get('target')
                except (json.JSONDecodeError, TypeError):
                    self.logger.warning(f"Could not parse action content: {content}")
                    continue
            
            features['action_type'] = action_type
            features['target_player'] = target_player

            label = self._determine_label(speaker_role, action_type, target_player, player_roles)

            training_samples.append({
                'features': json.dumps(features),
                'label': label,
                'game_id': game_history[0]['game_id'],
                'player_id': speaker_id
            })
            
        self.logger.info(f"Successfully extracted {len(training_samples)} training samples.")
        return training_samples

    def _determine_label(self, speaker_role: str, action_type: str, target_player_id: Optional[str], player_roles: Dict[str, str]) -> int:
        """
        Determines a label for a given action based on game logic.
        Label '1' for a "correct" or "logical" action, '0' otherwise.
        """
        if not target_player_id:
            return 0 # Neutral label for actions without a target (e.g., speaking)

        target_role = player_roles.get(target_player_id)
        if not target_role:
            return 0 # Cannot determine correctness if target role is unknown

        is_wolf_speaker = 'wolf' in speaker_role.lower()
        is_villager_speaker = 'villager' in speaker_role.lower()
        is_seer_speaker = 'seer' in speaker_role.lower()

        is_wolf_target = 'wolf' in target_role.lower()
        
        # Define "correct" actions
        correct_action = False
        if action_type == 'kill' and is_wolf_speaker and not is_wolf_target:
            correct_action = True  # Wolf killing a non-wolf
        elif action_type == 'vote':
            if (is_villager_speaker or is_seer_speaker) and is_wolf_target:
                correct_action = True # Good guy voting for a wolf
            elif is_wolf_speaker and not is_wolf_target:
                correct_action = True # Wolf voting for a non-wolf
        elif action_type == 'check' and is_seer_speaker:
            correct_action = True # Seer checking anyone is always a useful action

        return 1 if correct_action else 0

    def collect_and_store_data(self, game_id: str):
        """
        Main method to fetch history, extract features/labels, and store them in the database.
        """
        self.logger.info(f"Starting data collection and storage for game_id: {game_id}")
        conn = self._connect()
        if not conn:
            return

        history = self.fetch_game_history(game_id)
        if not history:
            self.logger.warning(f"No game history found for {game_id}. Aborting.")
            return
            
        player_roles = self.fetch_player_roles(game_id)
        if not player_roles:
            self.logger.warning(f"No player roles found for {game_id}. Cannot generate labeled data.")
            return

        training_data = self.extract_features_and_labels(history, player_roles)
        if not training_data:
            self.logger.warning("No training data was extracted.")
            return

        try:
            with conn:
                cursor = conn.cursor()
                # Clear old data for this game to prevent duplicates
                cursor.execute("DELETE FROM TrainingData WHERE game_id = ?", (game_id,))
                self.logger.info(f"Cleared old training data for game_id: {game_id}.\n")

                for sample in training_data:
                    cursor.execute(
                        """
                        INSERT INTO TrainingData (game_id, player_id, features, label, created_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (sample['game_id'], sample['player_id'], sample['features'], sample['label'], datetime.now().isoformat())
                    )
                self.logger.info(f"Stored {len(training_data)} new training samples for game_id: {game_id}.")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to store training data: {e}")

if __name__ == '__main__':
    # This is an example of how to use the collector.
    # It requires a populated database with game history and player profiles.
    db_path = '../../data/game.db'
    game_to_process = 'game_001' # Change this to a valid game_id in your database

    print(f"Running Data Collector for game: {game_to_process}")
    
    # 1. Initialize the collector
    collector = TrainingDataCollector(db_path=db_path)
    
    # 2. Run the collection process
    # This will fetch data, process it, and save it to the TrainingData table.
    collector.collect_and_store_data(game_to_process)

    # 3. Verify the results (optional)
    print("\nVerifying stored data...")
    try:
        con = sqlite3.connect(db_path)
        df = pd.read_sql_query(f"SELECT * FROM TrainingData WHERE game_id = '{game_to_process}'", con)
        con.close()
        if not df.empty:
            print(f"Successfully stored {len(df)} samples.")
            print("Sample features:")
            print(pd.json_normalize(df['features'].apply(json.loads)).head())
            print("\nSample labels:")
            print(df['label'].head())
        else:
            print("No data was stored. Check logs for warnings or errors.")
    except Exception as e:
        print(f"Could not verify data. Error: {e}")
