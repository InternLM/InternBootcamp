#!/bin/bash

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/mole_bootcamp/configs/mole_instruction_config.yaml \
    --output-dir internbootcamp/bootcamps/mole_bootcamp/data/mole_bootcamp/ \
    --split-samples train:100000,test:0 \
    --shuffle
