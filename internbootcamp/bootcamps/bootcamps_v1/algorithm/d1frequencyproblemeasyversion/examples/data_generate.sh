#!/bin/bash

# D1frequencyproblemeasyversion数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/d1frequencyproblemeasyversion/configs/D1frequencyproblemeasyversion_instruction_config.yaml \
    --output-dir data/D1frequencyproblemeasyversion/ \
    --split-samples train:1000,test:100 \
    --shuffle
