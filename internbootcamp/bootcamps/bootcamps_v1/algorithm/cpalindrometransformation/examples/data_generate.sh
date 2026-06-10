#!/bin/bash

# Cpalindrometransformation数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/cpalindrometransformation/configs/Cpalindrometransformation_instruction_config.yaml \
    --output-dir data/Cpalindrometransformation/ \
    --split-samples train:1000,test:100 \
    --shuffle
