#!/bin/bash

# Dchallengesinschool41数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/logical_reasoning/dchallengesinschool41/configs/Dchallengesinschool41_instruction_config.yaml \
    --output-dir data/Dchallengesinschool41/ \
    --split-samples train:1000,test:100 \
    --shuffle
