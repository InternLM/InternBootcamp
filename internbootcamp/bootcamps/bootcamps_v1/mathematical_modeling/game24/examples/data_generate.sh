#!/bin/bash

# Game24数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/game24/configs/game24_instruction_config.yaml \
    --output-dir data/game24/ \
    --split-samples train:1000,test:100 \
    --shuffle
