#!/bin/bash

# Ccheckposts数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/ccheckposts/configs/Ccheckposts_instruction_config.yaml \
    --output-dir data/Ccheckposts/ \
    --split-samples train:1000,test:100 \
    --shuffle
