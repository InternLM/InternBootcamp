#!/bin/bash

# Ctrailinglovesorloeufs数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/ctrailinglovesorloeufs/configs/Ctrailinglovesorloeufs_instruction_config.yaml \
    --output-dir data/Ctrailinglovesorloeufs/ \
    --split-samples train:1000,test:100 \
    --shuffle
