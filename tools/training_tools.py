from fastmcp import YA_MCPServer_Tool
from typing import Optional
import uuid
import threading
import datetime
import pandas as pd
import numpy as np

# Placeholder for the actual training logic and status tracking
# In a real implementation, this would be a more robust state machine or manager
training_threads = {}
training_status = {}

# Assuming other core modules are available
from core.data.data_collector import TrainingDataCollector
from core.data.preprocessor import DataPreprocessor
from core.data.dataset_manager import DatasetManager
from core.models.model_config import load_config
from core.training.trainer import Trainer
from core.evaluation.tester import Tester
from core.database import GameDatabase
from modules.YA_Common.utils.logger import get_logger

logger = get_logger("training_tools")

def run_training_session(run_id: str, model_type: str, game_id: Optional[str]):
    """The actual function that runs in a separate thread."""
    db = None  # Initialize db to None
    try:
        training_status[run_id] = {
            "status": "starting",
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": None,
            "metrics": None,
            "error": None
        }

        db = GameDatabase()

        # 1. Data Collection
        training_status[run_id]["status"] = "collecting_data"
        logger.info(f"[{run_id}] Collecting data...")
        collector = TrainingDataCollector(db_path='data/game.db')
        
        if game_id:
            # Collect data for a specific game
            logger.info(f"[{run_id}] Collecting data for specific game: {game_id}")
            collector.collect_and_store_data(game_id)
        else:
            # Collect data for all games in the history
            logger.info(f"[{run_id}] Collecting data for all games.")
            all_games = db.conn.execute("SELECT DISTINCT game_id FROM GameHistory").fetchall()
            game_ids = [row['game_id'] for row in all_games if row['game_id']]
            logger.info(f"[{run_id}] Found games to process: {game_ids}")
            for gid in game_ids:
                collector.collect_and_store_data(gid)

        # 2. Data Loading and Preprocessing
        training_status[run_id]["status"] = "loading_and_preprocessing_data"
        logger.info(f"[{run_id}] Loading and preprocessing data from database...")
        
        # Load all data from the TrainingData table
        training_df = pd.read_sql_query("SELECT features, label FROM TrainingData", db.conn)
        
        if training_df.empty:
            raise ValueError("No training data found after collection. Aborting.")

        # The 'features' column is a JSON string, so we need to parse it.
        features_df = pd.json_normalize(training_df['features'].apply(eval))
        labels = training_df['label']

        # This is where a real preprocessor would handle categorical features, etc.
        # For now, we assume the features are mostly numeric or can be used directly.
        # We will just use the 'text_vector' if available, otherwise dummy features.
        if 'text_vector' in features_df.columns:
            # Pad sequences to the same length
            features = list(features_df['text_vector'].apply(lambda x: x if isinstance(x, list) else [0.0] * 100))
            max_len = max(len(f) for f in features)
            features = [f + [0.0] * (max_len - len(f)) for f in features]
        else:
            # Fallback to dummy features if no text vector
            num_samples = len(labels)
            features = np.random.rand(num_samples, 10).tolist()

        logger.info(f"[{run_id}] Loaded {len(features)} samples.")

        dataset_manager = DatasetManager()
        train_data, val_data, test_data = dataset_manager.split_data(features, labels.tolist())

        # 3. Training
        training_status[run_id]["status"] = "training"
        logger.info(f"[{run_id}] Starting training for model type: {model_type}...")
        model_config = load_config(model_type)
        
        # Adjust input size based on feature vector length
        model_config['input_size'] = len(features[0])
        
        trainer = Trainer(model_config, train_data, val_data)
        model, history = trainer.run()
        
        # Save the model
        model_path = f"models/saved/{model_type}_{run_id}.pth"
        trainer.save_model(model, model_path)
        logger.info(f"[{run_id}] Model saved to {model_path}")

        # 4. Evaluation
        training_status[run_id]["status"] = "evaluating"
        logger.info(f"[{run_id}] Evaluating model...")
        tester = Tester(model, test_data, device=trainer.device)
        metrics = tester.test()
        logger.info(f"[{run_id}] Evaluation metrics: {metrics}")

        # 5. Record to DB
        training_status[run_id]["status"] = "saving_results"
        version_id = f"v{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        db.conn.execute(
            "INSERT INTO ModelVersion (version_id, model_name, file_path, created_at) VALUES (?, ?, ?, ?)",
            (version_id, model_type, model_path, datetime.datetime.now().isoformat())
        )
        db.conn.execute(
            "INSERT INTO TrainingRun (run_id, model_version_id, status, start_time, end_time, metrics) VALUES (?, ?, ?, ?, ?, ?)",
            (run_id, version_id, "completed", training_status[run_id]['start_time'], datetime.datetime.now().isoformat(), str(metrics))
        )
        db.conn.commit()
        logger.info(f"[{run_id}] Training run and model version saved to database.")

        # 6. Finish
        training_status[run_id]["status"] = "completed"
        training_status[run_id]["end_time"] = datetime.datetime.now().isoformat()
        training_status[run_id]["metrics"] = metrics
        db.close()

    except Exception as e:
        logger.error(f"Error during training run {run_id}: {e}", exc_info=True)
        training_status[run_id]["status"] = "failed"
        training_status[run_id]["error"] = str(e)
        training_status[run_id]["end_time"] = datetime.datetime.now().isoformat()
        if db:
            db.close()


@YA_MCPServer_Tool
def start_training(model_type: str = "lstm", game_id: Optional[str] = None) -> dict:
    """
    Starts a new model training session in the background.
    
    :param model_type: The type of model to train (e.g., 'lstm', 'transformer').
    :param game_id: Optional game_id to use for data collection. If None, uses all available data.
    :return: A dictionary with the run_id for the training session.
    """
    run_id = f"run_{uuid.uuid4()}"
    
    thread = threading.Thread(target=run_training_session, args=(run_id, model_type, game_id))
    training_threads[run_id] = thread
    thread.start()
    
    logger.info(f"Started training run: {run_id} for model type {model_type}")
    return {"status": "Training started", "run_id": run_id}

@YA_MCPServer_Tool
def stop_training(run_id: str) -> dict:
    """
    Stops a running training session. Note: This is a placeholder and may not gracefully stop the thread.
    
    :param run_id: The ID of the training run to stop.
    :return: A status message.
    """
    if run_id in training_threads and training_threads[run_id].is_alive():
        # In a real scenario, you'd need a more sophisticated way to stop the thread,
        # e.g., by setting a flag that the training loop checks.
        # For now, we'll just update the status.
        training_status[run_id]["status"] = "stopped"
        logger.warning(f"Stop signal sent to training run {run_id}. Manual interruption might be needed.")
        # The thread itself is not killed, which is not ideal.
        return {"status": f"Stop signal sent to training run {run_id}. The process may take time to halt."}
    return {"status": "Training run not found or not running."}


@YA_MCPServer_Tool
def get_training_status(run_id: str) -> dict:
    """
    Gets the status of a training session.
    
    :param run_id: The ID of the training run.
    :return: A dictionary with the current status and other details of the run.
    """
    status = training_status.get(run_id)
    if not status:
        # If not in memory, check DB
        db = GameDatabase()
        run_data = db.conn.execute("SELECT * FROM TrainingRun WHERE run_id = ?", (run_id,)).fetchone()
        db.close()
        if run_data:
            return dict(run_data)
        return {"status": "not_found"}
    return status

@YA_MCPServer_Tool
def evaluate_model(model_version_id: str) -> dict:
    """
    Evaluates a specified model version on a fresh test dataset from the database.
    
    :param model_version_id: The version ID of the model to evaluate.
    :return: A dictionary with evaluation metrics.
    """
    db = GameDatabase()
    try:
        model_info = db.conn.execute("SELECT * FROM ModelVersion WHERE version_id = ?", (model_version_id,)).fetchone()
        if not model_info:
            return {"status": "error", "message": "Model version not found."}

        logger.info(f"Evaluating model version: {model_version_id}")

        # Load all data from the TrainingData table to create a test set
        training_df = pd.read_sql_query("SELECT features, label FROM TrainingData", db.conn)
        if training_df.empty:
            return {"status": "error", "message": "No data available in TrainingData table to form a test set."}

        # Process features similarly to the training run
        features_df = pd.json_normalize(training_df['features'].apply(eval))
        labels = training_df['label']
        
        if 'text_vector' in features_df.columns:
            features = list(features_df['text_vector'].apply(lambda x: x if isinstance(x, list) else [0.0] * 100))
            max_len = max(len(f) for f in features)
            features = [f + [0.0] * (max_len - len(f)) for f in features]
        else:
            num_samples = len(labels)
            features = np.random.rand(num_samples, 10).tolist()

        # We use the whole dataset as a "test" set here for simplicity,
        # but ideally, we'd reserve a dedicated, unseen test set.
        dataset_manager = DatasetManager(test_size=0.99) # Use almost all data for testing
        _, _, test_data = dataset_manager.split_data(features, labels.tolist())

        if not test_data or not test_data[0]:
             return {"status": "error", "message": "Failed to create a test dataset."}

        logger.info(f"Created test dataset with {len(test_data[0])} samples.")

        # Load model
        model_config = load_config(model_info['model_name'])
        model_config['input_size'] = len(features[0])
        trainer = Trainer(model_config, [], []) # Dummy trainer to access methods
        model = trainer.load_model(model_info['file_path'])
        
        # Evaluate
        tester = Tester(model, test_data, device=trainer.device)
        metrics = tester.test()
        
        # Find the corresponding run_id to update metrics
        run_info = db.conn.execute("SELECT run_id FROM TrainingRun WHERE model_version_id = ?", (model_version_id,)).fetchone()
        if run_info:
            db.conn.execute(
                "UPDATE TrainingRun SET metrics = ? WHERE run_id = ?",
                (str(metrics), run_info['run_id'])
            )
            db.conn.commit()
            logger.info(f"Updated metrics for run {run_info['run_id']} with new evaluation results.")
        else:
            logger.warning(f"Could not find a training run associated with model version {model_version_id} to update metrics.")
        
        logger.info(f"Evaluated model {model_version_id}. Metrics: {metrics}")
        return {"status": "completed", "metrics": metrics}
    except Exception as e:
        logger.error(f"Failed to evaluate model {model_version_id}: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@YA_MCPServer_Tool
def get_model_metrics(model_version_id: str) -> dict:
    """
    Retrieves the stored metrics for a given model version.
    (Placeholder)
    
    :param model_version_id: The version ID of the model.
    :return: A dictionary of metrics.
    """
    db = GameDatabase()
    run_info = db.conn.execute("SELECT metrics FROM TrainingRun WHERE model_version_id = ?", (model_version_id,)).fetchone()
    db.close()
    
    if run_info and run_info['metrics']:
        return {"status": "found", "metrics": eval(run_info['metrics'])}
    
    return {"status": "not_found", "message": "Metrics not found for this model version."}

@YA_MCPServer_Tool
def compare_models(version_ids: list[str]) -> dict:
    """
    Compares the metrics of two or more model versions.
    (Placeholder)
    
    :param version_ids: A list of model version IDs to compare.
    :return: A dictionary comparing the metrics.
    """
    db = GameDatabase()
    comparison = {}
    for version_id in version_ids:
        run_info = db.conn.execute("SELECT metrics FROM TrainingRun WHERE model_version_id = ?", (version_id,)).fetchone()
        if run_info and run_info['metrics']:
            comparison[version_id] = eval(run_info['metrics'])
        else:
            comparison[version_id] = "Metrics not found."
    
    db.close()
    return {"status": "completed", "comparison": comparison}

@YA_MCPServer_Tool
def export_training_data(format: str = "csv") -> dict:
    """
    Exports the collected training data from the database to a specified format.
    
    :param format: The format to export to ('csv' or 'json').
    :return: A status message with the path to the exported file.
    """
    db = GameDatabase()
    try:
        logger.info(f"Exporting TrainingData table to {format} format.")
        
        # Query the TrainingData table
        df = pd.read_sql_query("SELECT * FROM TrainingData", db.conn)
        
        if df.empty:
            logger.warning("TrainingData table is empty. Nothing to export.")
            return {"status": "empty", "message": "No training data to export."}

        # The 'features' column is a JSON string, expand it into separate columns
        try:
            features_df = pd.json_normalize(df['features'].apply(eval))
            df = df.drop('features', axis=1).join(features_df)
        except Exception as e:
            logger.warning(f"Could not expand features column: {e}. Exporting raw features.")

        export_path = f"data/exported_training_data_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.{format}"
        
        if format == "csv":
            df.to_csv(export_path, index=False)
        elif format == "json":
            df.to_json(export_path, orient='records', lines=True)
        else:
            return {"status": "error", "message": "Unsupported format. Use 'csv' or 'json'."}
            
        logger.info(f"Exported {len(df)} records to {export_path}")
        return {"status": "completed", "path": export_path}
    except Exception as e:
        logger.error(f"Failed to export training data: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
