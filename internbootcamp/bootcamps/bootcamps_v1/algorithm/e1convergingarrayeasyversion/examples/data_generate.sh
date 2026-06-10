#!/bin/bash

# E1convergingarrayeasyversion数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/e1convergingarrayeasyversion/configs/E1convergingarrayeasyversion_instruction_config.yaml \
    --output-dir data/E1convergingarrayeasyversion/ \
    --split-samples train:1000,test:100 \
    --shuffle
