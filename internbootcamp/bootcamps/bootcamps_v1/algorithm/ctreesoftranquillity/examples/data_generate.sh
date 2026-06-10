#!/bin/bash

# Ctreesoftranquillity数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/ctreesoftranquillity/configs/Ctreesoftranquillity_instruction_config.yaml \
    --output-dir data/Ctreesoftranquillity/ \
    --split-samples train:1000,test:100 \
    --shuffle
