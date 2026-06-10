#!/bin/bash

# Esubsetsums数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/esubsetsums/configs/Esubsetsums_instruction_config.yaml \
    --output-dir data/Esubsetsums/ \
    --split-samples train:1000,test:100 \
    --shuffle
