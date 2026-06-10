#!/bin/bash

# Koroperationunicode20ac数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/koroperationunicode20ac/configs/korOperationUnicode20ac_instruction_config.yaml \
    --output-dir data/korOperationUnicode20ac/ \
    --split-samples train:1000,test:100 \
    --shuffle
