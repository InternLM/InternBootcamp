#!/bin/bash

# Kakuro数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/kakuro/configs/kakuro_instruction_config.yaml \
    --output-dir data/kakuro/ \
    --split-samples train:1000,test:100 \
    --shuffle
