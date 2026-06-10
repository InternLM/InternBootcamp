#!/bin/bash

# Cvoting数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/logical_reasoning/cvoting/configs/Cvoting_instruction_config.yaml \
    --output-dir data/Cvoting/ \
    --split-samples train:1000,test:100 \
    --shuffle
