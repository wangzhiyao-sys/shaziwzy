import sqlite3
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from modules.YA_Common.utils.logger import get_logger
import json

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
                dataset_id TEXT NOT NULL,
                features TEXT NOT NULL, 
                label TEXT NOT NULL,     
                game_id TEXT,           
                created_at TEXT NOT NULL,
                annotated_by TEXT DEFAULT 'system'  
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ModelVersion (
                version_id TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                model_type TEXT NOT NULL,  
                model_path TEXT NOT NULL,  
                run_id TEXT,               
                metrics TEXT,              
                description TEXT,
                created_at TEXT NOT NULL,
                last_evaluated TEXT       
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TrainingRun (
                run_id TEXT PRIMARY KEY,
                model_type TEXT NOT NULL,
                dataset_id TEXT NOT NULL,
                hyper_params TEXT NOT NULL,  
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT NOT NULL,        
                progress REAL DEFAULT 0.0,   
                model_version_id TEXT        
            )
        """)

        self.conn.commit()
        logger.info("Database tables initialized")

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

     # ========== 新增：TrainingData表CRUD方法 ==========
    def create_training_data(
        self,
        dataset_id: str,
        features: Dict[str, Any],
        label: str,
        game_id: Optional[str] = None,
        annotated_by: str = "system"
    ):
        """新增训练样本"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO TrainingData (dataset_id, features, label, game_id, created_at, annotated_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            dataset_id,
            json.dumps(features, ensure_ascii=False),
            label,
            game_id,
            datetime.now().isoformat(),
            annotated_by
        ))
        self.conn.commit()

    def get_training_data(
        self,
        dataset_id: Optional[str] = None,
        label: Optional[str] = None,
        game_id: Optional[str] = None,
        limit: int = 10000
    ) -> List[Dict[str, Any]]:
        """查询训练数据，支持多条件过滤"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM TrainingData WHERE 1=1"
        params = []
        if dataset_id:
            query += " AND dataset_id = ?"
            params.append(dataset_id)
        if label:
            query += " AND label = ?"
            params.append(label)
        if game_id:
            query += " AND game_id = ?"
            params.append(game_id)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        # 解析JSON特征
        result = []
        for row in rows:
            row_dict = dict(row)
            row_dict["features"] = json.loads(row_dict["features"])
            result.append(row_dict)
        return result

    # ========== 新增：ModelVersion表CRUD方法 ==========
    def create_model_version(
        self,
        version_id: str,
        model_name: str,
        model_type: str,
        model_path: str,
        run_id: Optional[str] = None,
        description: str = "",
        created_at: Optional[str] = None
    ):
        """新增模型版本记录"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO ModelVersion (version_id, model_name, model_type, model_path, run_id, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            version_id,
            model_name,
            model_type,
            model_path,
            run_id,
            description,
            created_at or datetime.now().isoformat()
        ))
        self.conn.commit()

    def get_model_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """查询单个模型版本"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ModelVersion WHERE version_id = ?", (version_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_model_version(
        self,
        version_id: str,
        metrics: Optional[str] = None,
        last_evaluated: Optional[str] = None
    ):
        """更新模型指标和评估时间"""
        cursor = self.conn.cursor()
        updates = []
        params = []
        if metrics:
            updates.append("metrics = ?")
            params.append(metrics)
        if last_evaluated:
            updates.append("last_evaluated = ?")
            params.append(last_evaluated)
        if not updates:
            return
        params.append(version_id)
        cursor.execute(f"UPDATE ModelVersion SET {', '.join(updates)} WHERE version_id = ?", params)
        self.conn.commit()

    # ========== 新增：TrainingRun表CRUD方法 ==========
    def create_training_run(
        self,
        run_id: str,
        model_type: str,
        dataset_id: str,
        hyper_params: str,
        start_time: Optional[str] = None,
        status: str = "running"
    ):
        """新增训练任务记录"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO TrainingRun (run_id, model_type, dataset_id, hyper_params, start_time, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            model_type,
            dataset_id,
            hyper_params,
            start_time or datetime.now().isoformat(),
            status
        ))
        self.conn.commit()

    def get_training_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """查询单个训练任务"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM TrainingRun WHERE run_id = ?", (run_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_training_run(
        self,
        run_id: str,
        status: Optional[str] = None,
        end_time: Optional[str] = None,
        progress: Optional[float] = None,
        model_version_id: Optional[str] = None
    ):
        """更新训练任务状态/进度/关联模型"""
        cursor = self.conn.cursor()
        updates = []
        params = []
        if status:
            updates.append("status = ?")
            params.append(status)
        if end_time:
            updates.append("end_time = ?")
            params.append(end_time)
        if progress is not None:
            updates.append("progress = ?")
            params.append(progress)
        if model_version_id:
            updates.append("model_version_id = ?")
            params.append(model_version_id)
        if not updates:
            return
        params.append(run_id)
        cursor.execute(f"UPDATE TrainingRun SET {', '.join(updates)} WHERE run_id = ?", params)
        self.conn.commit()

    def close(self):
        self.conn.close()
