#!/bin/bash

# Emikeandfoam数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/unknown/emikeandfoam/configs/Emikeandfoam_instruction_config.yaml \
    --output-dir data/Emikeandfoam/ \
    --split-samples train:1000,test:100 \
    --shuffle
