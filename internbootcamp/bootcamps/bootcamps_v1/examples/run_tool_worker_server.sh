python -m internbootcamp.utils.tool_server.cli \
  --port 8080 \
  --mode worker \
  --bootcamp_registry internbootcamp/examples/configs/old_bootcamps_registry.jsonl \
  --num_workers 8 \
  --master_url http://10.130.131.233:8080 