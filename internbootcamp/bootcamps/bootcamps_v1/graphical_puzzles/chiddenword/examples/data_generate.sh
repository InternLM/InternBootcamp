#!/bin/bash

# Chiddenword数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/chiddenword/configs/Chiddenword_instruction_config.yaml \
    --output-dir data/Chiddenword/ \
    --split-samples train:1000,test:100 \
    --shuffle
