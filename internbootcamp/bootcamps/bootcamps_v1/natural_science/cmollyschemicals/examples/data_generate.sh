#!/bin/bash

# Cmollyschemicals数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/natural_science/cmollyschemicals/configs/Cmollyschemicals_instruction_config.yaml \
    --output-dir data/Cmollyschemicals/ \
    --split-samples train:1000,test:100 \
    --shuffle
