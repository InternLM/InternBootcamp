#!/bin/bash

# Bbehhyperbaton数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/language_analysis/bbehhyperbaton/configs/BBEHHyperbaton_instruction_config.yaml \
    --output-dir data/BBEHHyperbaton/ \
    --split-samples train:1000,test:100 \
    --shuffle
