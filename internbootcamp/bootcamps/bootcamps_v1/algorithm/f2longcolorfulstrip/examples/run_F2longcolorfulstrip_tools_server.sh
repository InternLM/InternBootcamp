#!/bin/bash

# F2longcolorfulstrip工具服务器启动脚本

python -m internbootcamp.utils.auto_server_creator \
    --tools_yaml_path internbootcamp/bootcamps/bootcamps_v1/algorithm/f2longcolorfulstrip/configs/F2longcolorfulstrip_tool_config.yaml \
    --log_dir data/F2longcolorfulstrip/F2longcolorfulstrip_tool_server_logs/ \
    --port 16384 \
    --num_workers 8 \
    --test_servers \
    --keep_running \
    --timeout_per_query 600
