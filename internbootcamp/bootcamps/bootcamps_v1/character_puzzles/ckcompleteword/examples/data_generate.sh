#!/bin/bash

# Ckcompleteword数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/character_puzzles/ckcompleteword/configs/Ckcompleteword_instruction_config.yaml \
    --output-dir data/Ckcompleteword/ \
    --split-samples train:1000,test:100 \
    --shuffle
