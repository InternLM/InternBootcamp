#!/bin/bash

# Koroperationunicode25cb数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/koroperationunicode25cb/configs/korOperationUnicode25cb_instruction_config.yaml \
    --output-dir data/korOperationUnicode25cb/ \
    --split-samples train:1000,test:100 \
    --shuffle
