#!/bin/bash

# E1twilightandancientscrolleasierversion数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/e1twilightandancientscrolleasierversion/configs/E1twilightandancientscrolleasierversion_instruction_config.yaml \
    --output-dir data/E1twilightandancientscrolleasierversion/ \
    --split-samples train:1000,test:100 \
    --shuffle
