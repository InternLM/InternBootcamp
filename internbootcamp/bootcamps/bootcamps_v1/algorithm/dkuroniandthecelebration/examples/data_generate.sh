#!/bin/bash

# Dkuroniandthecelebration数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/dkuroniandthecelebration/configs/Dkuroniandthecelebration_instruction_config.yaml \
    --output-dir data/Dkuroniandthecelebration/ \
    --split-samples train:1000,test:100 \
    --shuffle
