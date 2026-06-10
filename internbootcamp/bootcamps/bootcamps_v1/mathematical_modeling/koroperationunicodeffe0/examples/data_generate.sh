#!/bin/bash

# Koroperationunicodeffe0数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/koroperationunicodeffe0/configs/korOperationUnicodeffe0_instruction_config.yaml \
    --output-dir data/korOperationUnicodeffe0/ \
    --split-samples train:1000,test:100 \
    --shuffle
