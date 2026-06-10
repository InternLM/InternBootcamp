#!/bin/bash

# Eplayingwithsuperglue数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/logical_reasoning/eplayingwithsuperglue/configs/Eplayingwithsuperglue_instruction_config.yaml \
    --output-dir data/Eplayingwithsuperglue/ \
    --split-samples train:1000,test:100 \
    --shuffle
