#!/bin/bash

# Crussianroulette数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/logical_reasoning/crussianroulette/configs/Crussianroulette_instruction_config.yaml \
    --output-dir data/Crussianroulette/ \
    --split-samples train:1000,test:100 \
    --shuffle
