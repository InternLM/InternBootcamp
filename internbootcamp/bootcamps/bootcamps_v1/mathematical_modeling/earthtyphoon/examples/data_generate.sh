#!/bin/bash

# Earthtyphoon数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/earthtyphoon/configs/earthtyphoon_instruction_config.yaml \
    --output-dir data/earthtyphoon/ \
    --split-samples train:1000,test:100 \
    --shuffle
