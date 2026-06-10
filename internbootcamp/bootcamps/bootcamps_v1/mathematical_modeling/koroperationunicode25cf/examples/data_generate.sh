#!/bin/bash

# Koroperationunicode25cf数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/koroperationunicode25cf/configs/korOperationUnicode25cf_instruction_config.yaml \
    --output-dir data/korOperationUnicode25cf/ \
    --split-samples train:1000,test:100 \
    --shuffle
