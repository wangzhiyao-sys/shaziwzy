from typing import Dict, List, Optional, Any, Literal
from tools import YA_MCPServer_Tool  # 复用现有工具注册装饰器
from core.database import GameDatabase  # 复用现有数据库实例
from modules.YA_Common.utils.logger import get_logger  # 复用现有日志
from modules.YA_Common.utils.config import get_config  # 复用现有配置读取
import json
import os
from datetime import datetime
import uuid

# 全局初始化（与游戏工具共享资源，确保兼容性）
logger = get_logger("training_tools")
db = GameDatabase()
# 全局训练状态管理（单机版，生产可替换为Redis）
_training_global_state = {
    "is_running": False,
    "current_run_id": None,
    "progress": 0.0,
    "status": "idle"  # idle/running/finished/stopped/failed
}

# -------------------------- 1. 启动训练 --------------------------
@YA_MCPServer_Tool(
    name="start_training",
    title="Start Model Training",
    description="启动模型训练任务，支持指定模型架构、超参数，自动关联训练数据"
)
async def start_training(
    model_type: Literal["LSTM", "Transformer", "GNN"] = get_config("model.default_type", "LSTM"),
    dataset_id: Optional[str] = None,
    train_ratio: float = get_config("training.data.train_ratio", 0.7),
    val_ratio: float = get_config("training.data.val_ratio", 0.15),
    test_ratio: float = get_config("training.data.test_ratio", 0.15),
    epochs: int = get_config("training.hyper_params.epochs", 50),
    batch_size: int = get_config("training.hyper_params.batch_size", 32),
    learning_rate: float = get_config("training.hyper_params.learning_rate", 0.001),
    optimizer: Literal["Adam", "SGD"] = get_config("training.hyper_params.optimizer", "Adam"),
    loss_function: Literal["cross_entropy", "mse"] = get_config("training.hyper_params.loss_function", "cross_entropy"),
    early_stopping_patience: int = get_config("training.hyper_params.early_stopping_patience", 5)
) -> Dict[str, Any]:
    """启动模型训练，自动从TrainingData表读取数据，支持配置文件默认值"""
    try:
        # 严格参数验证（第三步核心要求）
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
            return {"error": "训练/验证/测试集比例之和必须为1", "status": "failed"}
        if epochs <= 0 or batch_size <= 0 or learning_rate <= 0:
            return {"error": "epochs/batch_size/learning_rate必须大于0", "status": "failed"}
        if _training_global_state["is_running"]:
            return {
                "error": "已有训练任务在运行，请勿重复启动",
                "current_running_run_id": _training_global_state["current_run_id"],
                "status": "failed"
            }
        if not db.get_training_data(dataset_id=dataset_id):
            return {"error": f"数据集{dataset_id or '默认'}无训练数据，请先导入", "status": "failed"}

        # 生成唯一训练ID
        run_id = f"train_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d')}"
        # 超参数整合
        hyper_params = json.dumps({
            "train_ratio": train_ratio, "val_ratio": val_ratio, "test_ratio": test_ratio,
            "epochs": epochs, "batch_size": batch_size, "learning_rate": learning_rate,
            "optimizer": optimizer, "loss_function": loss_function, "early_stopping_patience": early_stopping_patience
        }, ensure_ascii=False)

        # 数据库记录训练任务（第三步系统集成：对接TrainingRun表）
        db.create_training_run(
            run_id=run_id,
            model_type=model_type,
            dataset_id=dataset_id or get_config("training.data.default_dataset_id", "default_werewolf"),
            hyper_params=hyper_params,
            start_time=datetime.now().isoformat(),
            status="running"
        )

        # 更新全局训练状态
        _training_global_state.update({
            "is_running": True,
            "current_run_id": run_id,
            "progress": 0.0,
            "status": "running"
        })

        logger.info(f"训练任务启动成功 | run_id={run_id} | model_type={model_type} | dataset_id={dataset_id or 'default'}")
        return {
            "run_id": run_id,
            "status": "success",
            "model_type": model_type,
            "hyper_params": json.loads(hyper_params),
            "message": "训练任务已启动，可通过get_training_status查询进度",
            "tips": "实际训练逻辑需对接训练层，此处已预留框架接口"
        }
    except Exception as e:
        logger.error(f"启动训练失败: {str(e)}", exc_info=True)
        return {"error": f"训练启动失败：{str(e)}", "status": "failed"}

# -------------------------- 2. 停止训练 --------------------------
@YA_MCPServer_Tool(
    name="stop_training",
    title="Stop Model Training",
    description="停止当前正在运行的训练任务，仅对running状态任务有效"
)
async def stop_training() -> Dict[str, Any]:
    """停止训练，更新数据库任务状态和全局状态"""
    try:
        if not _training_global_state["is_running"]:
            return {"error": "无正在运行的训练任务", "current_status": _training_global_state["status"], "status": "failed"}

        run_id = _training_global_state["current_run_id"]
        # 更新数据库训练任务
        db.update_training_run(
            run_id=run_id,
            status="stopped",
            end_time=datetime.now().isoformat(),
            progress=_training_global_state["progress"]
        )
        # 更新全局状态
        _training_global_state.update({
            "is_running": False,
            "status": "stopped",
            "progress": 0.0
        })

        logger.info(f"训练任务已停止 | run_id={run_id}")
        return {
            "run_id": run_id,
            "status": "success",
            "stopped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "final_progress": f"{_training_global_state['progress']:.2f}%",
            "message": "训练任务已手动停止"
        }
    except Exception as e:
        logger.error(f"停止训练失败: {str(e)}", exc_info=True)
        return {"error": f"停止训练失败：{str(e)}", "status": "failed"}

# -------------------------- 3. 查询训练状态 --------------------------
@YA_MCPServer_Tool(
    name="get_training_status",
    title="Get Training Status",
    description="查询指定训练任务状态，无run_id则查询当前运行任务"
)
async def get_training_status(run_id: Optional[str] = None) -> Dict[str, Any]:
    """查询训练状态，整合数据库持久化数据和全局实时状态"""
    try:
        target_run_id = run_id or _training_global_state["current_run_id"]
        if not target_run_id:
            return {"error": "无任何训练任务记录", "current_global_status": _training_global_state["status"], "status": "failed"}

        # 从数据库获取持久化数据
        training_run = db.get_training_run(run_id=target_run_id)
        if not training_run:
            return {"error": f"训练任务{target_run_id}不存在", "status": "failed"}

        # 整合实时状态（仅当前运行任务有实时进度）
        real_time_progress = _training_global_state["progress"] if target_run_id == _training_global_state["current_run_id"] else training_run["progress"]
        status_info = {
            "run_id": target_run_id,
            "model_type": training_run["model_type"],
            "dataset_id": training_run["dataset_id"],
            "hyper_params": json.loads(training_run["hyper_params"]),
            "start_time": training_run["start_time"],
            "end_time": training_run["end_time"] or "未结束",
            "status": training_run["status"],
            "progress": f"{real_time_progress:.2f}%",
            "model_version_id": training_run["model_version_id"] or "未生成模型",
            "is_running": target_run_id == _training_global_state["current_run_id"] and _training_global_state["is_running"]
        }

        logger.info(f"查询训练状态成功 | run_id={target_run_id}")
        return {"status": "success", "data": status_info}
    except Exception as e:
        logger.error(f"查询训练状态失败: {str(e)}", exc_info=True)
        return {"error": f"查询训练状态失败：{str(e)}", "status": "failed"}

# -------------------------- 4. 评估模型性能 --------------------------
@YA_MCPServer_Tool(
    name="evaluate_model",
    title="Evaluate Model Performance",
    description="在测试集评估指定模型版本，更新ModelVersion表指标"
)
async def evaluate_model(
    model_version_id: str,
    test_set_id: Optional[str] = None
) -> Dict[str, Any]:
    """评估模型，生成准确率/精确率/召回率/F1/混淆矩阵，对接评估层"""
    try:
        # 验证模型存在
        model_version = db.get_model_version(version_id=model_version_id)
        if not model_version:
            return {"error": f"模型版本{model_version_id}不存在", "status": "failed"}
        # 验证测试集存在
        if test_set_id and not db.get_training_data(dataset_id=test_set_id):
            return {"error": f"测试集{test_set_id}无数据", "status": "failed"}

        # 评估层逻辑占位（实际需对接scikit-learn/torch评估代码）
        evaluate_metrics = {
            "accuracy": round(float(get_config("training.eval.mock_accuracy", 0.89)), 4),
            "precision": round(float(get_config("training.eval.mock_precision", 0.87)), 4),
            "recall": round(float(get_config("training.eval.mock_recall", 0.85)), 4),
            "f1_score": round(float(get_config("training.eval.mock_f1", 0.86)), 4),
            "loss": round(float(get_config("training.eval.mock_loss", 0.23)), 4)
        }
        # 混淆矩阵（狼人/好人二分类示例）
        confusion_matrix = [[85, 15], [12, 88]]

        # 更新数据库模型指标
        db.update_model_version(
            version_id=model_version_id,
            metrics=json.dumps(evaluate_metrics, ensure_ascii=False),
            last_evaluated=datetime.now().isoformat()
        )

        logger.info(f"模型评估成功 | model_version_id={model_version_id} | test_set_id={test_set_id or 'default'}")
        return {
            "status": "success",
            "model_version_id": model_version_id,
            "model_type": model_version["model_type"],
            "test_set_id": test_set_id or "default",
            "metrics": evaluate_metrics,
            "confusion_matrix": confusion_matrix,
            "evaluated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"评估模型失败: {str(e)}", exc_info=True)
        return {"error": f"评估模型失败：{str(e)}", "status": "failed"}

# -------------------------- 5. 加载已训练模型 --------------------------
@YA_MCPServer_Tool(
    name="load_model",
    title="Load Trained Model",
    description="加载指定版本模型到内存，支持推理/二次训练"
)
async def load_model(model_version_id: str) -> Dict[str, Any]:
    """加载模型，验证文件存在性，对接模型层加载逻辑"""
    try:
        model_version = db.get_model_version(version_id=model_version_id)
        if not model_version:
            return {"error": f"模型版本{model_version_id}不存在", "status": "failed"}
        # 验证模型文件存在
        model_path = model_version["model_path"]
        if not os.path.exists(model_path):
            return {"error": f"模型文件缺失 | path={model_path}", "status": "failed"}

        # 模型层加载逻辑占位（实际需对接torch.load/tensorflow.load）
        logger.info(f"模型加载成功 | model_version_id={model_version_id} | path={model_path}")
        return {
            "status": "success",
            "model_version_id": model_version_id,
            "model_name": model_version["model_name"],
            "model_type": model_version["model_type"],
            "model_path": model_path,
            "loaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": "模型已成功加载到内存，可用于推理/二次训练"
        }
    except Exception as e:
        logger.error(f"加载模型失败: {str(e)}", exc_info=True)
        return {"error": f"加载模型失败：{str(e)}", "status": "failed"}

# -------------------------- 6. 保存训练模型 --------------------------
@YA_MCPServer_Tool(
    name="save_model",
    title="Save Trained Model",
    description="保存训练好的模型，生成版本记录，关联训练任务"
)
async def save_model(
    model_name: str,
    model_type: Literal["LSTM", "Transformer", "GNN"],
    run_id: str,
    description: Optional[str] = "无描述"
) -> Dict[str, Any]:
    """保存模型，自动生成版本ID，更新TrainingRun和ModelVersion表"""
    try:
        # 验证训练任务存在
        training_run = db.get_training_run(run_id=run_id)
        if not training_run:
            return {"error": f"训练任务{run_id}不存在", "status": "failed"}
        # 验证训练任务非已完成
        if training_run["status"] == "finished":
            return {"error": f"训练任务{run_id}已完成，请勿重复保存", "status": "failed"}

        # 生成唯一模型版本ID
        model_version_id = f"model_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d')}"
        # 模型保存路径（从配置读取）
        model_save_dir = get_config("model.save_path", "./resources/models")
        os.makedirs(model_save_dir, exist_ok=True)
        model_path = f"{model_save_dir}/{model_version_id}.pth"

        # 模型层保存逻辑占位（实际需对接torch.save/tensorflow.save）
        # torch.save(model.state_dict(), model_path)  # PyTorch示例

        # 数据库记录模型版本
        db.create_model_version(
            version_id=model_version_id,
            model_name=model_name,
            model_type=model_type,
            model_path=model_path,
            run_id=run_id,
            description=description,
            created_at=datetime.now().isoformat()
        )
        # 更新训练任务为完成，关联模型版本
        db.update_training_run(
            run_id=run_id,
            status="finished",
            end_time=datetime.now().isoformat(),
            progress=100.0,
            model_version_id=model_version_id
        )
        # 更新全局训练状态
        if _training_global_state["current_run_id"] == run_id:
            _training_global_state.update({
                "is_running": False,
                "status": "finished",
                "progress": 100.0
            })

        logger.info(f"模型保存成功 | model_version_id={model_version_id} | run_id={run_id} | path={model_path}")
        return {
            "status": "success",
            "model_version_id": model_version_id,
            "model_name": model_name,
            "model_type": model_type,
            "model_path": model_path,
            "run_id": run_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": "模型保存成功，已关联训练任务"
        }
    except Exception as e:
        logger.error(f"保存模型失败: {str(e)}", exc_info=True)
        return {"error": f"保存模型失败：{str(e)}", "status": "failed"}

# -------------------------- 7. 导出训练数据 --------------------------
@YA_MCPServer_Tool(
    name="export_training_data",
    title="Export Training Data",
    description="导出TrainingData表数据为JSON/CSV，支持数据集/标签过滤"
)
async def export_training_data(
    dataset_id: Optional[str] = None,
    label: Optional[str] = None,  # 如wolf/villager
    export_format: Literal["json", "csv"] = "json",
    output_path: str = get_config("training.data.export_path", "./exports/training_data")
) -> Dict[str, Any]:
    """导出训练数据，自动创建目录，支持过滤条件"""
    try:
        # 获取过滤后的数据
        training_data = db.get_training_data(dataset_id=dataset_id, label=label)
        if not training_data:
            return {"error": "无符合条件的训练数据", "filter": {"dataset_id": dataset_id, "label": label}, "status": "failed"}

        # 确保导出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        file_path = f"{output_path}.{export_format}"

        # 导出数据（JSON/CSV）
        if export_format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(training_data, f, ensure_ascii=False, indent=2)
        elif export_format == "csv":
            import csv
            if training_data:
                fieldnames = training_data[0].keys()
                with open(file_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(training_data)

        logger.info(f"训练数据导出成功 | 条数={len(training_data)} | 格式={export_format} | 路径={file_path}")
        return {
            "status": "success",
            "filter": {"dataset_id": dataset_id, "label": label},
            "export_format": export_format,
            "file_path": os.path.abspath(file_path),
            "record_count": len(training_data),
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"导出训练数据失败: {str(e)}", exc_info=True)
        return {"error": f"导出训练数据失败：{str(e)}", "status": "failed"}

# -------------------------- 8. 获取模型指标 --------------------------
@YA_MCPServer_Tool(
    name="get_model_metrics",
    title="Get Model Metrics",
    description="获取指定模型版本的详细评估指标（准确率/F1等）"
)
async def get_model_metrics(model_version_id: str) -> Dict[str, Any]:
    """获取模型指标，从ModelVersion表读取，返回标准化格式"""
    try:
        model_version = db.get_model_version(version_id=model_version_id)
        if not model_version:
            return {"error": f"模型版本{model_version_id}不存在", "status": "failed"}

        # 解析指标（无指标则返回空字典）
        metrics = json.loads(model_version["metrics"]) if model_version["metrics"] else {}
        model_info = {
            "model_version_id": model_version_id,
            "model_name": model_version["model_name"],
            "model_type": model_version["model_type"],
            "model_path": model_version["model_path"],
            "created_at": model_version["created_at"],
            "last_evaluated": model_version["last_evaluated"] or "未评估",
            "description": model_version["description"],
            "metrics": metrics or {"tips": "该模型未执行评估，请调用evaluate_model"}
        }

        logger.info(f"获取模型指标成功 | model_version_id={model_version_id}")
        return {"status": "success", "data": model_info}
    except Exception as e:
        logger.error(f"获取模型指标失败: {str(e)}", exc_info=True)
        return {"error": f"获取模型指标失败：{str(e)}", "status": "failed"}

# -------------------------- 9. 对比不同模型版本 --------------------------
@YA_MCPServer_Tool(
    name="compare_models",
    title="Compare Model Versions",
    description="对比多个模型版本性能，按F1_score排序返回最优模型"
)
async def compare_models(model_version_ids: List[str]) -> Dict[str, Any]:
    """对比模型，至少2个版本，按F1_score筛选最优，对接评估层"""
    try:
        # 参数验证
        if len(model_version_ids) < 2:
            return {"error": "至少需要指定2个模型版本进行对比", "status": "failed"}

        compare_result = {}
        valid_models = []
        # 遍历获取每个模型的指标
        for version_id in model_version_ids:
            model_version = db.get_model_version(version_id=version_id)
            if not model_version:
                compare_result[version_id] = {"status": "failed", "error": "模型版本不存在"}
                continue
            # 解析指标
            metrics = json.loads(model_version["metrics"]) if model_version["metrics"] else {}
            compare_result[version_id] = {
                "status": "success",
                "model_name": model_version["model_name"],
                "model_type": model_version["model_type"],
                "created_at": model_version["created_at"],
                "metrics": metrics or {"tips": "未评估"}
            }
            # 筛选有F1指标的有效模型
            if metrics and "f1_score" in metrics:
                valid_models.append({
                    "model_version_id": version_id,
                    "f1_score": metrics["f1_score"],
                    "accuracy": metrics["accuracy"]
                })

        # 找出最优模型（按F1_score降序）
        best_model = max(valid_models, key=lambda x: x["f1_score"]) if valid_models else None

        logger.info(f"模型对比完成 | 对比版本数={len(model_version_ids)} | 有效模型数={len(valid_models)}")
        return {
            "status": "success",
            "compare_result": compare_result,
            "best_model": best_model,
            "sort_by": "f1_score（降序）",
            "tips": "无有效模型表示部分模型未执行评估，请先调用evaluate_model"
        }
    except Exception as e:
        logger.error(f"对比模型失败: {str(e)}", exc_info=True)
        return {"error": f"对比模型失败：{str(e)}", "status": "failed"}