#!/bin/bash

# Conlinemeeting数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/logical_reasoning/conlinemeeting/configs/Conlinemeeting_instruction_config.yaml \
    --output-dir data/Conlinemeeting/ \
    --split-samples train:1000,test:100 \
    --shuffle
