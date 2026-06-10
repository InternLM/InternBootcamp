#!/bin/bash

# Eregionseparation数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/mathematical_modeling/eregionseparation/configs/Eregionseparation_instruction_config.yaml \
    --output-dir data/Eregionseparation/ \
    --split-samples train:1000,test:100 \
    --shuffle
