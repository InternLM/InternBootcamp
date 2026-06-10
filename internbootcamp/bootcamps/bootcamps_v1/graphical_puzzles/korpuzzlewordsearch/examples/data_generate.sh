#!/bin/bash

# Korpuzzlewordsearch数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/korpuzzlewordsearch/configs/korPuzzleWordSearch_instruction_config.yaml \
    --output-dir data/korPuzzleWordSearch/ \
    --split-samples train:1000,test:100 \
    --shuffle
