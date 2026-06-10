# InternBootcamp Web Service

InternBootcamp 的前后端可视化平台，提供数据生成、模型评测与结果分析功能。

## 快速开始

### 安装依赖

```bash
cd /path/to/internbootcamp_v2
pip install -r internbootcamp/web_service/requirements_frontend.txt
```

### 启动服务

**推荐方式：使用启动脚本**

```bash
# 终端1：启动后端
cd internbootcamp/web_service
./start_backend.sh

# 终端2：启动前端
cd internbootcamp/web_service
./start_frontend.sh
```

**手动启动**

```bash
# 启动后端
cd /path/to/internbootcamp_v2
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn internbootcamp.web_service.backend.main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端
cd /path/to/internbootcamp_v2
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
streamlit run internbootcamp/web_service/frontend/streamlit_app.py
```

### 访问服务

- **前端界面**: http://localhost:8501
- **后端API文档**: http://localhost:8000/docs
- **后端API文档（静态md版）**: 查看 [API.md](./API.md)

## 主要功能

### 数据生成
- 配置指令生成器，批量生成评测数据
- 实时查看生成进度

### 模型评测
- 配置评测参数，支持多种评测格式
- 实时查看评测结果和进度

### 结果分析
- 分析评测结果文件（支持标准格式和迭代格式）
- **按需加载**：分页查看样本，支持大文件（数万个样本）
- **排序功能**：按分数、成功状态、Token数排序
- **迭代分析**：自动识别最高分迭代，标记最佳迭代
- 提供详细的统计和可视化

### 任务管理
- 查看任务状态和日志
- 支持取消和删除任务

## 技术栈

- **后端**: FastAPI + Pydantic + asyncio
- **前端**: Streamlit + Plotly + Pandas
- **通信**: RESTful API + JSON

## 常见问题

**后端连接失败**
- 确保后端服务正在运行（端口 8000）
- 检查端口是否被占用

**前端缓存问题**
- 点击侧边栏的"🔄 清除缓存"按钮，然后刷新页面

## 开发说明

### 运行要求
- Python 3.8+
- 在项目根目录下运行
- 确保 `PYTHONPATH` 包含项目根目录

### Import 路径规范
所有 import 使用完整路径：
```python
from internbootcamp.web_service.backend.models.schemas import TaskInfo
from internbootcamp.web_service.frontend.utils.api_client import APIClient
```

## 相关文档

- [API 接口文档](./API.md) - 后端 API 详细说明

