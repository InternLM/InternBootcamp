#!/bin/bash

# Korpuzzle24points数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/korpuzzle24points/configs/korPuzzle24Points_instruction_config.yaml \
    --output-dir data/korPuzzle24Points/ \
    --split-samples train:1000,test:100 \
    --shuffle
