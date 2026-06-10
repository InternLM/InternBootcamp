#!/bin/bash

# Egameontree数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/egameontree/configs/Egameontree_instruction_config.yaml \
    --output-dir data/Egameontree/ \
    --split-samples train:1000,test:100 \
    --shuffle
