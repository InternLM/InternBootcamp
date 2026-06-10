#!/bin/bash

# Ccycle数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/ccycle/configs/Ccycle_instruction_config.yaml \
    --output-dir data/Ccycle/ \
    --split-samples train:1000,test:100 \
    --shuffle
