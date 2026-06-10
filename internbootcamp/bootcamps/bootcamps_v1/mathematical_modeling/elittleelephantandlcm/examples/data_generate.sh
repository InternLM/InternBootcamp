#!/bin/bash

# Elittleelephantandlcm数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/elittleelephantandlcm/configs/Elittleelephantandlcm_instruction_config.yaml \
    --output-dir data/Elittleelephantandlcm/ \
    --split-samples train:1000,test:100 \
    --shuffle
