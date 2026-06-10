#!/bin/bash

# Bpiet数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/bpiet/configs/Bpiet_instruction_config.yaml \
    --output-dir data/Bpiet/ \
    --split-samples train:1000,test:100 \
    --shuffle
