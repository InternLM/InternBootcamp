python -m internbootcamp.utils.batch_data_generation \
    --bootcamp-registry internbootcamp/examples/bootcamp_registry/bootcamp_registry_of_filtered_v1_bootcamps.jsonl \
    --output-dir data/filtered_v1_bootcamps \
    --split-samples train:1000,test:16 \
    --max-workers 64 \
    --log-level DEBUG \
    --continue-on-error \
    --concat-files \
    --no-tool