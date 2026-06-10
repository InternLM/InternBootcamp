#!/bin/bash

# Koroperationunicode0033数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/koroperationunicode0033/configs/korOperationUnicode0033_instruction_config.yaml \
    --output-dir data/korOperationUnicode0033/ \
    --split-samples train:1000,test:100 \
    --shuffle
