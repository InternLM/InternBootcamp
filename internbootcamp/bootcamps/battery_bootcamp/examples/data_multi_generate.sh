python -m internbootcamp.utils.batch_data_generation \
    --bootcamp-registry configs/bootcamp_registry.jsonl \
    --max-workers 5 \
    --output-dir data/batch_generated/ \
    --split-samples train:2000,test:1 \
    --concat-files \
    --continue-on-error