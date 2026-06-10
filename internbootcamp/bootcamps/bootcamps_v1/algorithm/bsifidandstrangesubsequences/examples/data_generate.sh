#!/bin/bash

# Bsifidandstrangesubsequences数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/bsifidandstrangesubsequences/configs/Bsifidandstrangesubsequences_instruction_config.yaml \
    --output-dir data/Bsifidandstrangesubsequences/ \
    --split-samples train:1000,test:100 \
    --shuffle
