#!/bin/bash

# Cgameontree数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/cgameontree/configs/Cgameontree_instruction_config.yaml \
    --output-dir data/Cgameontree/ \
    --split-samples train:1000,test:100 \
    --shuffle
