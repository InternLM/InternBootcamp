#!/bin/bash

# Koroperationunicode25b3数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/koroperationunicode25b3/configs/korOperationUnicode25b3_instruction_config.yaml \
    --output-dir data/korOperationUnicode25b3/ \
    --split-samples train:1000,test:100 \
    --shuffle
