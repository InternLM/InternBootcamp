#!/bin/bash

# Crectangles数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/crectangles/configs/Crectangles_instruction_config.yaml \
    --output-dir data/Crectangles/ \
    --split-samples train:1000,test:100 \
    --shuffle
