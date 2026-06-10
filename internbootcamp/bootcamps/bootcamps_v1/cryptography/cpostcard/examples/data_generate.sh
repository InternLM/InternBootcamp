#!/bin/bash

# Cpostcard数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/cryptography/cpostcard/configs/Cpostcard_instruction_config.yaml \
    --output-dir data/Cpostcard/ \
    --split-samples train:1000,test:100 \
    --shuffle
