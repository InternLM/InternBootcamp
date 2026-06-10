#!/bin/bash

# Medcalculator数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/natural_science/medcalculator/configs/medcalculator_instruction_config.yaml \
    --output-dir data/medcalculator/ \
    --split-samples train:1000,test:100 \
    --shuffle
