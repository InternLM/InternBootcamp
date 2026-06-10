#!/bin/bash

# Bstring数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/character_puzzles/bstring/configs/Bstring_instruction_config.yaml \
    --output-dir data/Bstring/ \
    --split-samples train:1000,test:100 \
    --shuffle
