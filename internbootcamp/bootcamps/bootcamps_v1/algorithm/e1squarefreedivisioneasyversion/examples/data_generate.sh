#!/bin/bash

# E1squarefreedivisioneasyversion数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/e1squarefreedivisioneasyversion/configs/E1squarefreedivisioneasyversion_instruction_config.yaml \
    --output-dir data/E1squarefreedivisioneasyversion/ \
    --split-samples train:1000,test:100 \
    --shuffle
