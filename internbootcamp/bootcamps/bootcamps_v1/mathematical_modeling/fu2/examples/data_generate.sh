#!/bin/bash

# Fu2数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/fu2/configs/Fu2_instruction_config.yaml \
    --output-dir data/Fu2/ \
    --split-samples train:1000,test:100 \
    --shuffle
