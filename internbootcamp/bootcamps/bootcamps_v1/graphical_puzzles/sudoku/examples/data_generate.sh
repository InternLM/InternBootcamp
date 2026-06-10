#!/bin/bash

# Sudoku数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/sudoku/configs/sudoku_instruction_config.yaml \
    --output-dir data/sudoku/ \
    --split-samples train:1000,test:100 \
    --shuffle
