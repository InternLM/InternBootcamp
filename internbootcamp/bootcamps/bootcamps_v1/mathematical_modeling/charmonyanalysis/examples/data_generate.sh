#!/bin/bash

# Charmonyanalysis数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/charmonyanalysis/configs/Charmonyanalysis_instruction_config.yaml \
    --output-dir data/Charmonyanalysis/ \
    --split-samples train:1000,test:100 \
    --shuffle
