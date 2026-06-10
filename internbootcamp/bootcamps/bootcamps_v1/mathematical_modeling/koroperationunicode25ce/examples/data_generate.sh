#!/bin/bash

# Koroperationunicode25ce数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/koroperationunicode25ce/configs/korOperationUnicode25ce_instruction_config.yaml \
    --output-dir data/korOperationUnicode25ce/ \
    --split-samples train:1000,test:100 \
    --shuffle
