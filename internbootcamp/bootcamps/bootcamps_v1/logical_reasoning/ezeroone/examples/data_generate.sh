#!/bin/bash

# Ezeroone数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/logical_reasoning/ezeroone/configs/Ezeroone_instruction_config.yaml \
    --output-dir data/Ezeroone/ \
    --split-samples train:1000,test:100 \
    --shuffle
