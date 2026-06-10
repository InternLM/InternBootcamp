#!/bin/bash

# Ccycliccoloring数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/ccycliccoloring/configs/Ccycliccoloring_instruction_config.yaml \
    --output-dir data/Ccycliccoloring/ \
    --split-samples train:1000,test:100 \
    --shuffle
