#!/bin/bash

# Koroperationunicode203b数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/koroperationunicode203b/configs/korOperationUnicode203b_instruction_config.yaml \
    --output-dir data/korOperationUnicode203b/ \
    --split-samples train:1000,test:100 \
    --shuffle
