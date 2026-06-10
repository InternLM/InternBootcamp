#!/bin/bash

# Ctexteditor数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/ctexteditor/configs/Ctexteditor_instruction_config.yaml \
    --output-dir data/Ctexteditor/ \
    --split-samples train:1000,test:100 \
    --shuffle
