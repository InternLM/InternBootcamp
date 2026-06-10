#!/bin/bash

# Dgeneratingsets数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/dgeneratingsets/configs/Dgeneratingsets_instruction_config.yaml \
    --output-dir data/Dgeneratingsets/ \
    --split-samples train:1000,test:100 \
    --shuffle
