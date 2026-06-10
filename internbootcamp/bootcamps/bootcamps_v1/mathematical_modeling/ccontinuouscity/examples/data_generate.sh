#!/bin/bash

# Ccontinuouscity数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/ccontinuouscity/configs/Ccontinuouscity_instruction_config.yaml \
    --output-dir data/Ccontinuouscity/ \
    --split-samples train:1000,test:100 \
    --shuffle
