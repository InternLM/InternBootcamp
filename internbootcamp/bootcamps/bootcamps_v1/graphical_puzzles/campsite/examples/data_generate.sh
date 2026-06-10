#!/bin/bash

# Campsite数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/campsite/configs/campsite_instruction_config.yaml \
    --output-dir data/campsite/ \
    --split-samples train:1000,test:100 \
    --shuffle
