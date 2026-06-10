#!/bin/bash
# 启动 Streamlit 前端服务

echo "正在启动 InternBootcamp 前端服务..."

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 获取项目根目录（web_service 的父目录的父目录）
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 设置 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$PROJECT_ROOT"

echo "项目根目录: $PROJECT_ROOT"

# 启动 streamlit
streamlit run internbootcamp/web_service/frontend/streamlit_app.py

