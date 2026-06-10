#!/bin/bash

# Nonograms数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/nonograms/configs/nonograms_instruction_config.yaml \
    --output-dir data/nonograms/ \
    --split-samples train:1000,test:100 \
    --shuffle
