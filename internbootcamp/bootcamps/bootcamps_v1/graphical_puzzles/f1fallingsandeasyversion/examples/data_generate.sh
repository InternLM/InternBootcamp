#!/bin/bash

# F1fallingsandeasyversion数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/f1fallingsandeasyversion/configs/F1fallingsandeasyversion_instruction_config.yaml \
    --output-dir data/F1fallingsandeasyversion/ \
    --split-samples train:1000,test:100 \
    --shuffle
