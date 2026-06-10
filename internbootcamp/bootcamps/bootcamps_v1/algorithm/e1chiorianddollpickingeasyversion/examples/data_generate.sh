#!/bin/bash

# E1chiorianddollpickingeasyversion数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/e1chiorianddollpickingeasyversion/configs/E1chiorianddollpickingeasyversion_instruction_config.yaml \
    --output-dir data/E1chiorianddollpickingeasyversion/ \
    --split-samples train:1000,test:100 \
    --shuffle
