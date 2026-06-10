#!/bin/bash

# Asearchingforgraph数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/asearchingforgraph/configs/Asearchingforgraph_instruction_config.yaml \
    --output-dir data/Asearchingforgraph/ \
    --split-samples train:1000,test:100 \
    --shuffle
