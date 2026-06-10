#!/bin/bash

# Koroperationunicode25bd数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/koroperationunicode25bd/configs/korOperationUnicode25bd_instruction_config.yaml \
    --output-dir data/korOperationUnicode25bd/ \
    --split-samples train:1000,test:100 \
    --shuffle
