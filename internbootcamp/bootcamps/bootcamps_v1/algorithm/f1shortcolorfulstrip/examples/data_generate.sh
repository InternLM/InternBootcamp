#!/bin/bash

# F1shortcolorfulstrip数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/f1shortcolorfulstrip/configs/F1shortcolorfulstrip_instruction_config.yaml \
    --output-dir data/F1shortcolorfulstrip/ \
    --split-samples train:1000,test:100 \
    --shuffle
