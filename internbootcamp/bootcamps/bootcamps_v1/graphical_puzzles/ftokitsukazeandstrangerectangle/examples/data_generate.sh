#!/bin/bash

# Ftokitsukazeandstrangerectangle数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/ftokitsukazeandstrangerectangle/configs/Ftokitsukazeandstrangerectangle_instruction_config.yaml \
    --output-dir data/Ftokitsukazeandstrangerectangle/ \
    --split-samples train:1000,test:100 \
    --shuffle
