#!/bin/bash

# Koroperationunicode221e数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/koroperationunicode221e/configs/korOperationUnicode221e_instruction_config.yaml \
    --output-dir data/korOperationUnicode221e/ \
    --split-samples train:1000,test:100 \
    --shuffle
