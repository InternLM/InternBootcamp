#!/bin/bash

# Cpackagedelivery数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/cpackagedelivery/configs/Cpackagedelivery_instruction_config.yaml \
    --output-dir data/Cpackagedelivery/ \
    --split-samples train:1000,test:100 \
    --shuffle
