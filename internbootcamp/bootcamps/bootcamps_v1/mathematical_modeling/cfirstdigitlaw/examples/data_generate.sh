#!/bin/bash

# Cfirstdigitlaw数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/cfirstdigitlaw/configs/Cfirstdigitlaw_instruction_config.yaml \
    --output-dir data/Cfirstdigitlaw/ \
    --split-samples train:1000,test:100 \
    --shuffle
