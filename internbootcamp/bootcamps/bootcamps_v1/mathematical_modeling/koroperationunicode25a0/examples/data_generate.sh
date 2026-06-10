#!/bin/bash

# Koroperationunicode25a0数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/koroperationunicode25a0/configs/korOperationUnicode25a0_instruction_config.yaml \
    --output-dir data/korOperationUnicode25a0/ \
    --split-samples train:1000,test:100 \
    --shuffle
