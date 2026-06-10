# InternBootcamp 前后端平台 - 快速启动指南

## 🚀 5分钟快速开始

### 步骤 1: 安装依赖

```bash
# 进入项目目录
cd internbootcamp_v2

# 安装前后端依赖
pip install -r internbootcamp/web_service/requirements_frontend.txt
```

### 步骤 2: 启动后端服务

打开第一个终端窗口：

```bash
# 启动后端 API 服务（端口 8000）
./internbootcamp/web_service/start_backend.sh
```

等待看到以下提示：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 步骤 3: 启动前端服务

打开第二个终端窗口：

```bash
# 启动前端 Streamlit 应用（端口 8501）
./internbootcamp/web_service/start_frontend.sh
```

等待看到以下提示：
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### 步骤 4: 访问平台

在浏览器中打开：

- **前端界面**: http://localhost:8501
- **后端 API 文档**: http://localhost:8000/docs

## 📊 开始第一次评测

### 1. 准备数据

确保你有一个评测数据集（支持 `.jsonl`, `.json`, `.parquet` 格式），例如：

```bash
internbootcamp/bootcamps/example_bootcamp/data/test.jsonl
```

### 2. 在前端创建评测任务

1. 访问 http://localhost:8501
2. 选择"📊 模型评测"页面
3. 填写表单：
   - **数据集路径**: `internbootcamp/bootcamps/example_bootcamp/data/test.jsonl`
   - **API Key**: 你的模型 API 密钥
   - **模型名称**: `gpt-3.5-turbo`
   - **奖励计算器类**: `internbootcamp.bootcamps.example_bootcamp.example_reward_calculator.ExampleRewardCalculator`
4. 点击"🚀 开始评测"

### 3. 查看实时结果

评测开始后，你可以：

- ✅ 查看任务状态和进度
- ✅ 实时查看每个样本的评测结果
- ✅ 查看汇总统计和可视化图表
- ✅ 下载完整的评测报告

勾选"自动刷新"选项，页面会每 2 秒自动更新结果。

## 📝 数据生成示例

1. 选择"📝 数据生成"页面
2. 填写：
   - **指令配置文件**: `internbootcamp/bootcamps/example_bootcamp/configs/example_instruction_config.yaml`
   - **输出目录**: `outputs/my_data`
   - **数据集划分**: `train:10,test:2`
3. 点击"🚀 开始生成"

## 📁 分析已有评测结果

如果你已经有评测结果文件（JSONL 格式），可以直接分析而无需重新运行评测：

1. 选择"📁 结果分析"页面
2. 输入文件路径，或从"快速选择"中选择最近的评测文件
   - 例如：`outputs/evaluation/gpt-3.5-turbo/eval_results_20240115_143022.jsonl`
3. 点击"🔍 开始分析"
4. 查看完整的统计分析和可视化图表

**优势**：
- ✅ 无需关联任务，直接分析文件
- ✅ 支持分析历史评测结果
- ✅ 快速选择功能，自动扫描最近的评测文件
- ✅ 完整的可视化分析和样本筛选

## 🛠️ 常用操作

### 查看后端 API 文档

访问 http://localhost:8000/docs，你可以看到所有可用的 API 接口并进行测试。

### 查看任务列表

在前端选择"📋 任务管理"页面，可以查看所有历史任务。

### 下载评测结果

评测完成后，在"模型评测"页面的任务详情中，点击"📥 下载 JSONL" 或"📥 下载 CSV"按钮。

## 🔧 故障排除

### 问题 1: 后端启动失败

**错误**: `ModuleNotFoundError: No module named 'backend'`

**解决**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
./start_backend.sh
```

### 问题 2: 前端无法连接后端

**检查**:
1. 确保后端正在运行：`curl http://localhost:8000/health`
2. 检查 `.streamlit/secrets.toml` 中的 `BACKEND_URL`
3. 确保防火墙没有阻止 8000 端口

### 问题 3: 评测任务失败

**排查步骤**:
1. 在"任务管理"页面查看任务日志
2. 检查数据集路径是否正确
3. 检查 API Key 是否有效
4. 验证奖励计算器类路径是否正确

## 📚 更多文档

- **完整使用指南**: [docs/FRONTEND_GUIDE.md](docs/FRONTEND_GUIDE.md)
- **开发文档**: [README.md](README.md)
- **API 文档**: http://localhost:8000/docs

## 💡 提示

1. **并发控制**: 首次使用建议将"最大并发数"设为 1，避免 API 限流
2. **自动刷新**: 评测时勾选"自动刷新"可以实时查看结果
3. **结果下载**: 评测完成后及时下载结果，避免任务被删除
4. **日志查看**: 遇到问题时，查看任务日志可以快速定位错误

## 🎯 下一步

现在你已经成功启动了 InternBootcamp 平台，可以：

1. 📖 阅读 [完整使用指南](docs/FRONTEND_GUIDE.md) 了解更多功能
2. 🔨 创建自己的 Bootcamp（参考 README.md 第 3 节）
3. 📊 使用可视化功能深入分析评测结果
4. 🚀 开始你的模型训练之旅！

---

**需要帮助？** 查看 [docs/FRONTEND_GUIDE.md](docs/FRONTEND_GUIDE.md) 或提交 Issue。

