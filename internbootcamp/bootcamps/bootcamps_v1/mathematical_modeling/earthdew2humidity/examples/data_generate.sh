#!/bin/bash

# Earthdew2humidity数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/earthdew2humidity/configs/earthdew2humidity_instruction_config.yaml \
    --output-dir data/earthdew2humidity/ \
    --split-samples train:1000,test:100 \
    --shuffle
