#!/usr/bin/env python3
"""
分布式工具服务器主入口

支持直接通过 python -m 运行：
python -m internbootcamp.utils.tool_server.cli --mode unified --tools_yaml_path config.yaml --port 8000 --num_workers 5
"""

from .cli import main

if __name__ == "__main__":
    main() 