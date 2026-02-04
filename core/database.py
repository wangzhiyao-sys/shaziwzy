import sqlite3
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from modules.YA_Common.utils.logger import get_logger

logger = get_logger("database")


class GameDatabase:
    def __init__(self, db_path: str = "data/game.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS GameHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_num INTEGER NOT NULL,
                speaker TEXT NOT NULL,
                content TEXT NOT NULL,
                action_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                game_id TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS PlayerProfile (
                player_id TEXT PRIMARY KEY,
                role_assumed TEXT,
                suspicion_score REAL DEFAULT 0.0,
                personality TEXT,
                game_id TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS GameState (
                game_id TEXT PRIMARY KEY,
                current_round INTEGER DEFAULT 1,
                alive_players TEXT,
                game_status TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TrainingData (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT,
                player_id TEXT,
                features TEXT NOT NULL,
                label INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ModelVersion (
                version_id TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                description TEXT,
                file_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TrainingRun (
                run_id TEXT PRIMARY KEY,
                model_version_id TEXT,
                status TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                metrics TEXT,
                FOREIGN KEY (model_version_id) REFERENCES ModelVersion(version_id)
            )
        """)
        
        self.conn.commit()
        logger.info("Database tables initialized successfully.")

    def reset_database(self, game_id: Optional[str] = None):
        cursor = self.conn.cursor()
        if game_id:
            logger.info(f"Resetting game {game_id}.")
            cursor.execute("DELETE FROM GameHistory WHERE game_id=?", (game_id,))
            cursor.execute("DELETE FROM PlayerProfile WHERE game_id=?", (game_id,))
            cursor.execute("DELETE FROM GameState WHERE game_id=?", (game_id,))
        else:
            logger.info("Resetting all tables in the database.")
            cursor.execute("DELETE FROM GameHistory")
            cursor.execute("DELETE FROM PlayerProfile")
            cursor.execute("DELETE FROM GameState")
            cursor.execute("DELETE FROM TrainingData")
            cursor.execute("DELETE FROM ModelVersion")
            cursor.execute("DELETE FROM TrainingRun")
        self.conn.commit()
        logger.info("Database reset.")

    def record_event(
        self,
        round_num: int,
        speaker: str,
        content: str,
        action_type: str,
        game_id: Optional[str] = None
    ):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO GameHistory (round_num, speaker, content, action_type, timestamp, game_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (round_num, speaker, content, action_type, datetime.now().isoformat(), game_id))
        self.conn.commit()
        logger.debug(f"Recorded event: {action_type} by {speaker} in round {round_num}")

    def get_game_history(
        self,
        game_id: Optional[str] = None,
        round_num: Optional[int] = None,
        speaker: Optional[str] = None,
        action_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        query = "SELECT * FROM GameHistory WHERE 1=1"
        params = []
        
        if game_id:
            query += " AND game_id = ?"
            params.append(game_id)
        if round_num:
            query += " AND round_num = ?"
            params.append(round_num)
        if speaker:
            query += " AND speaker = ?"
            params.append(speaker)
        if action_type:
            query += " AND action_type = ?"
            params.append(action_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def update_player_profile(
        self,
        player_id: str,
        role_assumed: Optional[str] = None,
        suspicion_score: Optional[float] = None,
        personality: Optional[str] = None,
        game_id: Optional[str] = None
    ):
        cursor = self.conn.cursor()
        
        existing = cursor.execute(
            "SELECT * FROM PlayerProfile WHERE player_id = ?",
            (player_id,)
        ).fetchone()
        
        if existing:
            updates = []
            params = []
            if role_assumed is not None:
                updates.append("role_assumed = ?")
                params.append(role_assumed)
            if suspicion_score is not None:
                updates.append("suspicion_score = ?")
                params.append(suspicion_score)
            if personality is not None:
                updates.append("personality = ?")
                params.append(personality)
            if game_id is not None:
                updates.append("game_id = ?")
                params.append(game_id)
            
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(player_id)
            
            cursor.execute(
                f"UPDATE PlayerProfile SET {', '.join(updates)} WHERE player_id = ?",
                params
            )
        else:
            cursor.execute("""
                INSERT INTO PlayerProfile (player_id, role_assumed, suspicion_score, personality, game_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                player_id,
                role_assumed,
                suspicion_score if suspicion_score is not None else 0.0,
                personality,
                game_id,
                datetime.now().isoformat()
            ))
        
        self.conn.commit()
        logger.debug(f"Updated player profile: {player_id}")

    def get_player_profile(self, player_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM PlayerProfile WHERE player_id = ?", (player_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_player_profiles(self, game_id: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        if game_id:
            cursor.execute("SELECT * FROM PlayerProfile WHERE game_id = ?", (game_id,))
        else:
            cursor.execute("SELECT * FROM PlayerProfile")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def update_game_state(
        self,
        game_id: str,
        current_round: Optional[int] = None,
        alive_players: Optional[List[str]] = None,
        game_status: Optional[str] = None
    ):
        cursor = self.conn.cursor()
        
        existing = cursor.execute(
            "SELECT * FROM GameState WHERE game_id = ?",
            (game_id,)
        ).fetchone()
        
        if existing:
            updates = []
            params = []
            if current_round is not None:
                updates.append("current_round = ?")
                params.append(current_round)
            if alive_players is not None:
                updates.append("alive_players = ?")
                params.append(",".join(alive_players))
            if game_status is not None:
                updates.append("game_status = ?")
                params.append(game_status)
            
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(game_id)
            
            cursor.execute(
                f"UPDATE GameState SET {', '.join(updates)} WHERE game_id = ?",
                params
            )
        else:
            cursor.execute("""
                INSERT INTO GameState (game_id, current_round, alive_players, game_status, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                game_id,
                current_round if current_round is not None else 1,
                ",".join(alive_players) if alive_players else "",
                game_status,
                datetime.now().isoformat()
            ))
        
        self.conn.commit()

    def get_game_state(self, game_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM GameState WHERE game_id = ?", (game_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            if result.get("alive_players"):
                result["alive_players"] = result["alive_players"].split(",")
            return result
        return None

    def close(self):
        self.conn.close()
