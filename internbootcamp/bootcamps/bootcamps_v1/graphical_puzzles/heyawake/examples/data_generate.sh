#!/bin/bash

# Heyawake数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/heyawake/configs/heyawake_instruction_config.yaml \
    --output-dir data/heyawake/ \
    --split-samples train:1000,test:100 \
    --shuffle
