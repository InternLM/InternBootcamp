#!/bin/bash

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bot_bootcamp/configs/bot_instruction_config.yaml \
    --output-dir internbootcamp/bootcamps/bot_bootcamp/data/bot_bootcamp/ \
    --split-samples train:100000,test:0 \
    --shuffle
