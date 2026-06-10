#!/bin/bash

# Cacolourfulprospect数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/cacolourfulprospect/configs/Cacolourfulprospect_instruction_config.yaml \
    --output-dir data/Cacolourfulprospect/ \
    --split-samples train:1000,test:100 \
    --shuffle
