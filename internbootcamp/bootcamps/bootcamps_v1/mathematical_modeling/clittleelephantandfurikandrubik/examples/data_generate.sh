#!/bin/bash

# Clittleelephantandfurikandrubik数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/clittleelephantandfurikandrubik/configs/Clittleelephantandfurikandrubik_instruction_config.yaml \
    --output-dir data/Clittleelephantandfurikandrubik/ \
    --split-samples train:1000,test:100 \
    --shuffle
