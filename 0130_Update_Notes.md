新建文件：tools/training_tools.py（核心训练 MCP 工具，9 个工具全实现）
更新文件：core/database.py（新增 3 张训练表 + CRUD 方法）
更新文件：config.yaml（新增训练 / 模型 / 数据配置）
新建文件：tests/test_training_tools.py（训练工具单元测试，异步风格匹配现有测试）

狼人杀 AI 训练系统：已更新功能、体现及操作说明
本系统基于 MCP 框架完成了狼人杀 AI 训练全流程管理，覆盖 “训练数据准备→模型训练→训练监控→模型保存→数据导出” 的核心链路，所有操作结果持久化存储。
一、训练数据管理功能
具体功能：
向数据库插入带标签的训练样本（区分狼人 / 村民），为模型训练提供数据基础。
具体体现：
1.数据库：data/game.db的TrainingData表新增样本记录（含features特征、label标签）；
2.终端反馈：运行脚本后输出✅ 已向TrainingData表插入测试数据。
具体操作：
powershell
# 1. 激活环境+进入项目目录
conda activate mcp-polygame && cd E:\MCP-PolyGame-Agent
# 2. 运行测试脚本插入数据
python tests/test_training_tools.py
二、训练任务全生命周期管理
具体功能：
启动 LSTM 模型训练（支持自定义超参数）；
查询训练任务的进度、运行状态；
停止训练任务。
具体体现：
1.数据库：data/game.db的TrainingRun表新增训练任务记录（含任务 ID、模型类型、超参数）；
2.终端反馈：
启动训练后输出【start_training】返回结果: {"status": "success", "run_id": "train_xxx"}；
查询状态后输出任务进度、运行状态（如"progress": "0.00%"）。
具体操作：
powershell
# 前提：已启动MCP服务（终端执行python server.py）# 运行测试脚本自动执行训练任务操作
python tests/test_training_tools.py
三、模型版本管理功能
具体功能：
训练完成后自动保存模型，生成唯一版本 ID 并关联训练任务。
具体体现：
1.数据库：data/game.db的ModelVersion表新增模型记录（含版本 ID、模型路径）；
2.文件存储：resources/models目录生成模型文件（如model_xxx.pth）。
具体操作：
powershell
# 测试脚本自动调用save_model工具，无需额外命令
python tests/test_training_tools.py
四、训练数据导出功能
具体功能：
将TrainingData表的样本导出为 JSON 格式文件，便于后续数据分析。
具体体现：
文件存储：tests/exports目录生成test_training_data.json，包含结构化的特征与标签。
具体操作：
powershell
# 测试脚本自动调用export_training_data工具
python tests/test_training_tools.py

在 MCP Inspector（MCP服务的调试/管理工具）中，本次新增的训练系统功能核心体现和辅助体现及操作如下：
1. 核心体现：新增训练工具出现在 “Tools” 列表中
MCP 服务会将所有自定义工具（包括本次新增的训练类工具）注册到服务中，在 MCP Inspector 的Tools标签页可以查看这些工具：
操作：点击界面顶部标签栏的 “Tools” 选项卡；
体现：在工具列表中会显示本次新增的训练相关工具，包括：
start_training（启动模型训练）
get_training_status（查询训练任务状态）
save_model（保存训练模型）
export_training_data（导出训练数据）
2. 辅助体现：工具调用记录与结果反馈
若在 MCP Inspector 中调用这些训练工具，操作及体现如下：
选择某一训练工具（如start_training）；
在工具参数栏填写必要参数（如model_type: "LSTM"、epochs: 10）；
点击 “Execute” 执行工具调用；
在History面板中会新增该工具的调用记录；
面板会显示工具的返回结果（如start_training成功后返回run_id，失败则返回错误信息）。
3. 简而言之：本次新增的训练功能，在 MCP Inspector 中体现为 “Tools 标签页下新增的训练类工具”，可直接在该界面中调用这些工具、验证功能是否正常运行。