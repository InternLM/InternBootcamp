#!/bin/bash

# Koroperationunicodeffe1数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/logical_reasoning/koroperationunicodeffe1/configs/korOperationUnicodeffe1_instruction_config.yaml \
    --output-dir data/korOperationUnicodeffe1/ \
    --split-samples train:1000,test:100 \
    --shuffle
