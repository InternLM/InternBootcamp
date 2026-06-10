python -m internbootcamp.utils.tool_server.cli \
    --mode unified \
    --tools_yaml_path internbootcamp/bootcamps/bot_bootcamp/configs/bot_tool_config.yaml  \
    --num_workers 64 \
    --keep_running \
    --test_servers \
    --log_dir internbootcamp/bootcamps/bot_bootcamp/logs/
