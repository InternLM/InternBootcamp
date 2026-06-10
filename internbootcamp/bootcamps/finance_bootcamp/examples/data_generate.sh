#! /bin/bash

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/finance_bootcamp/configs/finance_instruction_config.yaml \
    --output-dir internbootcamp/bootcamps/finance_bootcamp/data/finance_bootcamp/ \
    --split-samples train:100000,test:100 \
    --shuffle \
