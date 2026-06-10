#! /bin/bash

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/escape_bootcamp/configs/escape_instruction_config.yaml \
    --output-dir internbootcamp/bootcamps/escape_bootcamp/data/escape_bootcamp/ \
    --split-samples train:100000,test:100 \
    --shuffle