#!/bin/bash

# Cgardenofthesun数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/cgardenofthesun/configs/Cgardenofthesun_instruction_config.yaml \
    --output-dir data/Cgardenofthesun/ \
    --split-samples train:1000,test:100 \
    --shuffle
