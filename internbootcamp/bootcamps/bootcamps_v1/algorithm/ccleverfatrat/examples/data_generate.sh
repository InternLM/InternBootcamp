#!/bin/bash

# Ccleverfatrat数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/ccleverfatrat/configs/Ccleverfatrat_instruction_config.yaml \
    --output-dir data/Ccleverfatrat/ \
    --split-samples train:1000,test:100 \
    --shuffle
