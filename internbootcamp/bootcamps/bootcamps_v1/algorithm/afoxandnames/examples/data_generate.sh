#!/bin/bash

# Afoxandnames数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/afoxandnames/configs/Afoxandnames_instruction_config.yaml \
    --output-dir data/Afoxandnames/ \
    --split-samples train:1000,test:100 \
    --shuffle
