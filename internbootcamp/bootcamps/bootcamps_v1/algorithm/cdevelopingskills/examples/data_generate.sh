#!/bin/bash

# Cdevelopingskills数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/cdevelopingskills/configs/Cdevelopingskills_instruction_config.yaml \
    --output-dir data/Cdevelopingskills/ \
    --split-samples train:1000,test:100 \
    --shuffle
