import asyncio
import json
import os
from typing import Dict
from mcp import ClientSession
from mcp.client.sse import sse_client

# 测试全局变量
TEST_RUN_ID = None
TEST_MODEL_VERSION_ID = None


async def test_tool(session, tool_name: str, params: Dict = None) -> Dict:
    """通用工具调用方法，统一返回格式"""
    params = params or {}
    result = await session.call_tool(tool_name, params)
    result_text = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
    result_data = json.loads(result_text) if isinstance(result_text, str) else result_text
    print(f"\n【{tool_name}】返回结果：")
    print(json.dumps(result_data, indent=2, ensure_ascii=False))
    return result_data


async def main():
    global TEST_RUN_ID, TEST_MODEL_VERSION_ID
    print("="*80)
    print("训练工具单元测试 | 请确保MCP服务已启动：http://127.0.0.1:12345")
    print("="*80)

    # 连接MCP服务
    try:
        async with sse_client(url="http://127.0.0.1:12345") as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("\n✅ MCP服务连接成功，开始测试训练工具...")

                # 1. 测试start_training（启动训练，修复字典键引号）
                train_result = await test_tool(session, "start_training", {
                    "model_type": "LSTM",
                    "epochs": 10,
                    "batch_size": 16
                })
                if train_result.get("status") == "success":
                    TEST_RUN_ID = train_result.get("run_id")

                # 2. 测试get_training_status（查询训练状态）
                await test_tool(session, "get_training_status", {"run_id": TEST_RUN_ID})

                # 3. 测试save_model（保存模型，关联训练任务，修复字典键引号）
                if TEST_RUN_ID:
                    save_result = await test_tool(session, "save_model", {
                        "model_name": "狼人检测模型-测试版",
                        "model_type": "LSTM",
                        "run_id": TEST_RUN_ID,
                        "description": "单元测试生成的模型，仅用于测试"
                    })
                    if save_result.get("status") == "success":
                        TEST_MODEL_VERSION_ID = save_result.get("model_version_id")

                # 4. 测试evaluate_model（评估模型）
                if TEST_MODEL_VERSION_ID:
                    await test_tool(session, "evaluate_model", {
                        "model_version_id": TEST_MODEL_VERSION_ID
                    })

                # 5. 测试get_model_metrics（获取模型指标）
                if TEST_MODEL_VERSION_ID:
                    await test_tool(session, "get_model_metrics", {
                        "model_version_id": TEST_MODEL_VERSION_ID
                    })

                # 6. 测试export_training_data（导出训练数据，修复字典键引号）
                # 先创建测试数据（模拟）
                from core.database import GameDatabase
                db = GameDatabase()
                db.create_training_data(
                    dataset_id="default_werewolf",
                    features={"suspicion_score": 0.85, "action_count": 5},
                    label="wolf",
                    game_id="test_game_001"
                )
                # 导出测试
                await test_tool(session, "export_training_data", {
                    "dataset_id": "default_werewolf",
                    "export_format": "json",
                    "output_path": "tests/exports/test_training_data"
                })

                # 7. 测试compare_models（对比模型，模拟两个版本，修复字典键引号）
                if TEST_MODEL_VERSION_ID:
                    await test_tool(session, "compare_models", {
                        "model_version_ids": [TEST_MODEL_VERSION_ID, f"model_test_{os.urandom(4).hex()}"]
                    })

                # 8. 测试load_model（加载模型，修复字典键引号）
                if TEST_MODEL_VERSION_ID:
                    await test_tool(session, "load_model", {
                        "model_version_id": TEST_MODEL_VERSION_ID
                    })

                # 9. 测试stop_training（停止训练）
                await test_tool(session, "stop_training")

                print("\n" + "="*80)
                print("✅ 所有训练工具测试完成！")
                print("="*80)

    except Exception as e:
        print(f"\n❌ 测试失败：{str(e)}")
        print("请检查：1.MCP服务是否启动 2.训练工具是否注册 3.数据库是否初始化")


if __name__ == "__main__":
    try:
        # 创建测试导出目录（简化路径）
        os.makedirs("tests/exports", exist_ok=True)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nℹ️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 运行失败：{str(e)}")