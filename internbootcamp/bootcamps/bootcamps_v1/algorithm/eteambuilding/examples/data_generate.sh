#!/bin/bash

# Eteambuilding数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/eteambuilding/configs/Eteambuilding_instruction_config.yaml \
    --output-dir data/Eteambuilding/ \
    --split-samples train:1000,test:100 \
    --shuffle
