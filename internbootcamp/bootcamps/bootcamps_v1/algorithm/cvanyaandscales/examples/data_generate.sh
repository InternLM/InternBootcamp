#!/bin/bash

# Cvanyaandscales数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/cvanyaandscales/configs/Cvanyaandscales_instruction_config.yaml \
    --output-dir data/Cvanyaandscales/ \
    --split-samples train:1000,test:100 \
    --shuffle
