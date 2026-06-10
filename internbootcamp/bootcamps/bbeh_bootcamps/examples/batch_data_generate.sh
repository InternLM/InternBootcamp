python -m internbootcamp.utils.batch_data_generation \
    --bootcamp-registry internbootcamp/bootcamps/bbeh_bootcamps/configs/bbeh_bootcamps_registry.jsonl \
    --output-dir internbootcamp/bootcamps/bbeh_bootcamps/data/gen \
    --split-samples train:0,test:32 \
    --max-workers 10 \
    --log-level DEBUG \
    --continue-on-error \
    --concat-files \
    --no-tool