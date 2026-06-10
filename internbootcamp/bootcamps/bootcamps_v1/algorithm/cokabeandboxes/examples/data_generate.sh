#!/bin/bash

# Cokabeandboxes数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/cokabeandboxes/configs/Cokabeandboxes_instruction_config.yaml \
    --output-dir data/Cokabeandboxes/ \
    --split-samples train:1000,test:100 \
    --shuffle
