#!/bin/bash

# Cmessy工具服务器启动脚本

python -m internbootcamp.utils.auto_server_creator \
    --tools_yaml_path internbootcamp/bootcamps/bootcamps_v1/algorithm/cmessy/configs/Cmessy_tool_config.yaml \
    --log_dir data/Cmessy/Cmessy_tool_server_logs/ \
    --port 16384 \
    --num_workers 8 \
    --test_servers \
    --keep_running \
    --timeout_per_query 600
