#!/bin/bash

# Dlcc数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/natural_science/dlcc/configs/Dlcc_instruction_config.yaml \
    --output-dir data/Dlcc/ \
    --split-samples train:1000,test:100 \
    --shuffle
