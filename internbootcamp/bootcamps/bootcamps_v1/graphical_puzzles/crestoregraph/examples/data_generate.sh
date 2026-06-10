#!/bin/bash

# Crestoregraph数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/crestoregraph/configs/Crestoregraph_instruction_config.yaml \
    --output-dir data/Crestoregraph/ \
    --split-samples train:1000,test:100 \
    --shuffle
