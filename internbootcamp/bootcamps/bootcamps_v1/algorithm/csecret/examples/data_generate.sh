#!/bin/bash

# Csecret数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/csecret/configs/Csecret_instruction_config.yaml \
    --output-dir data/Csecret/ \
    --split-samples train:1000,test:100 \
    --shuffle
