#!/usr/bin/env python3
"""
分布式工具服务器模块

提供Master-Worker架构的分布式工具服务器实现，支持：
- Master服务器：负责请求路由和Worker管理
- Worker服务器：负责执行具体的工具逻辑
- 统一服务器：在单机上同时运行Master和多个Worker

支持的运行模式：
1. master: 只启动Master服务器，等待Worker注册
2. worker: 启动Worker服务器并注册到指定的Master
3. unified: 在本地同时启动Master和多个Worker进程

使用示例：
```python
from internbootcamp.utils.tool_server import DistributedMasterServer, DistributedWorkerServer

# 启动Master服务器
master = DistributedMasterServer(tools_config, "0.0.0.0", 8000)
master.run()

# 启动Worker服务器
worker = DistributedWorkerServer(tools_config, "0.0.0.0", 8001, "worker_1", "http://master:8000")
worker.run()
```

命令行使用：
```bash
# 启动Master
python -m internbootcamp.utils.tool_server.cli --mode master --tools_yaml_path config.yaml --port 8000

# 启动Worker  
python -m internbootcamp.utils.tool_server.cli --mode worker --tools_yaml_path config.yaml --master_url http://master:8000 --port 8001 --num_workers 3

# 启动统一服务器
python -m internbootcamp.utils.tool_server.cli --mode unified --tools_yaml_path config.yaml --port 8000 --num_workers 5
```
"""

from .master_server import DistributedMasterServer
from .worker_server import DistributedWorkerServer
from .models import WorkerRegistrationData, CreateInput
from .utils import (
    load_tools_config,
    get_external_ip,
    find_available_port,
    update_tools_config_with_urls,
    extract_tool_names_from_config
)

__all__ = [
    "DistributedMasterServer",
    "DistributedWorkerServer", 
    "WorkerRegistrationData",
    "CreateInput",
    "load_tools_config",
    "get_external_ip",
    "find_available_port", 
    "update_tools_config_with_urls",
    "extract_tool_names_from_config"
]

__version__ = "1.0.0" 