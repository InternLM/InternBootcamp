#! /bin/bash

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/holdem_bootcamp/configs/holdem_instruction_config.yaml \
    --output-dir internbootcamp/bootcamps/holdem_bootcamp/data/holdem_bootcamp/ \
    --split-samples train:0,test:1 \
    --shuffle
