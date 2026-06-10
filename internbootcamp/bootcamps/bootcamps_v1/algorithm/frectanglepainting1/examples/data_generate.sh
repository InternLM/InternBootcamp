#!/bin/bash

# Frectanglepainting1数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/frectanglepainting1/configs/Frectanglepainting1_instruction_config.yaml \
    --output-dir data/Frectanglepainting1/ \
    --split-samples train:1000,test:100 \
    --shuffle
