#!/bin/bash

# D2optimalsubsequenceshardversion数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/d2optimalsubsequenceshardversion/configs/D2optimalsubsequenceshardversion_instruction_config.yaml \
    --output-dir data/D2optimalsubsequenceshardversion/ \
    --split-samples train:1000,test:100 \
    --shuffle
