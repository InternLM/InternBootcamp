#!/bin/bash

# Koroperationunicodeffe1工具服务器启动脚本

python -m internbootcamp.utils.auto_server_creator \
    --tools_yaml_path internbootcamp/bootcamps/bootcamps_v1/logical_reasoning/koroperationunicodeffe1/configs/korOperationUnicodeffe1_tool_config.yaml \
    --log_dir data/korOperationUnicodeffe1/korOperationUnicodeffe1_tool_server_logs/ \
    --port 16384 \
    --num_workers 8 \
    --test_servers \
    --keep_running \
    --timeout_per_query 600
