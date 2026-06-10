#!/bin/bash

# Arc工具服务器启动脚本

python -m internbootcamp.utils.distributed_server_creator \
    --tools_yaml_path internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/arc/configs/arc_tool_config.yaml \
    --log_dir data/arc/arc_tool_server_logs/ \
    --port 16384 \
    --mode unified \
    --num_workers 8 \
    --test_servers \
    --keep_running \
    --timeout_per_query 600
