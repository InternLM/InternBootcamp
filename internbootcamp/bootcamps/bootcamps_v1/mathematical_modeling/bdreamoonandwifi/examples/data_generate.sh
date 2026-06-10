#!/bin/bash

# Bdreamoonandwifi数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/bdreamoonandwifi/configs/Bdreamoonandwifi_instruction_config.yaml \
    --output-dir data/Bdreamoonandwifi/ \
    --split-samples train:1000,test:100 \
    --shuffle
