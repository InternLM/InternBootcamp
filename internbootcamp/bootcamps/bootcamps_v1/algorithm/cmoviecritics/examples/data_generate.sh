#!/bin/bash

# Cmoviecritics数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/cmoviecritics/configs/Cmoviecritics_instruction_config.yaml \
    --output-dir data/Cmoviecritics/ \
    --split-samples train:1000,test:100 \
    --shuffle
