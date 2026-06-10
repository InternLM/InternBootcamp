#!/bin/bash

# Korpuzzleskyscrapers数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/korpuzzleskyscrapers/configs/korPuzzleSkyscrapers_instruction_config.yaml \
    --output-dir data/korPuzzleSkyscrapers/ \
    --split-samples train:1000,test:100 \
    --shuffle
