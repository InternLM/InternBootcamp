#!/bin/bash

# Cwateringflowers数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/cwateringflowers/configs/Cwateringflowers_instruction_config.yaml \
    --output-dir data/Cwateringflowers/ \
    --split-samples train:1000,test:100 \
    --shuffle
