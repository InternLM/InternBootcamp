#!/bin/bash

# Cmashmokhandreverseoperation数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/cmashmokhandreverseoperation/configs/Cmashmokhandreverseoperation_instruction_config.yaml \
    --output-dir data/Cmashmokhandreverseoperation/ \
    --split-samples train:1000,test:100 \
    --shuffle
