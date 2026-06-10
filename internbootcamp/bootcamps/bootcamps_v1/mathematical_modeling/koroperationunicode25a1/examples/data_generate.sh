#!/bin/bash

# Koroperationunicode25a1数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/koroperationunicode25a1/configs/korOperationUnicode25a1_instruction_config.yaml \
    --output-dir data/korOperationUnicode25a1/ \
    --split-samples train:1000,test:100 \
    --shuffle
