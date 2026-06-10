#!/bin/bash

# Cconnect数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/cconnect/configs/Cconnect_instruction_config.yaml \
    --output-dir data/Cconnect/ \
    --split-samples train:1000,test:100 \
    --shuffle
