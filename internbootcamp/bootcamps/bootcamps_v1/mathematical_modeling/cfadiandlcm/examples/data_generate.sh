#!/bin/bash

# Cfadiandlcm数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/cfadiandlcm/configs/Cfadiandlcm_instruction_config.yaml \
    --output-dir data/Cfadiandlcm/ \
    --split-samples train:1000,test:100 \
    --shuffle
