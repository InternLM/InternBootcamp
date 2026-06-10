#!/bin/bash

# Korlogicpropositionallogicformalization数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/logical_reasoning/korlogicpropositionallogicformalization/configs/korLogicPropositionalLogicFormalization_instruction_config.yaml \
    --output-dir data/korLogicPropositionalLogicFormalization/ \
    --split-samples train:1000,test:100 \
    --shuffle
