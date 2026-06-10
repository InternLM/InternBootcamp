python -m internbootcamp.utils.tool_server.cli \
    --mode unified \
    --tools_yaml_path internbootcamp/bootcamps/mole_bootcamp/configs/mole_tool_config.yaml  \
    --num_workers 64 \
    --keep_running \
    --test_servers \
    --log_dir internbootcamp/bootcamps/mole_bootcamp/logs/
