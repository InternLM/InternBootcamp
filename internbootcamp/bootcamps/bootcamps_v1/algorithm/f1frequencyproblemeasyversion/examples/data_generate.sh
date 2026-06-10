#!/bin/bash

# F1frequencyproblemeasyversion数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/f1frequencyproblemeasyversion/configs/F1frequencyproblemeasyversion_instruction_config.yaml \
    --output-dir data/F1frequencyproblemeasyversion/ \
    --split-samples train:1000,test:100 \
    --shuffle
