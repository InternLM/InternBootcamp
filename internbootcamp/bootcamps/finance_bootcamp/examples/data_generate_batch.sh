#! /bin/bash

python -m internbootcamp.utils.batch_data_generation \
    --bootcamp-registry internbootcamp/bootcamps/finance_bootcamp/configs/bootcamp_registry.jsonl \
    --max-workers 8 \
    --output-dir data/finance_bootcamp/ \
    --split-samples train:100000,test:1000 \
    --concat-files \
    --continue-on-error
