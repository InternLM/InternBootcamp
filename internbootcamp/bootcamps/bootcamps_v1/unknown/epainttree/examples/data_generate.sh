#!/bin/bash

# Epainttree数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/unknown/epainttree/configs/Epainttree_instruction_config.yaml \
    --output-dir data/Epainttree/ \
    --split-samples train:1000,test:100 \
    --shuffle
