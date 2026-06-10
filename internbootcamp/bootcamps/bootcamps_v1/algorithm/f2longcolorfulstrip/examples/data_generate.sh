#!/bin/bash

# F2longcolorfulstrip数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/f2longcolorfulstrip/configs/F2longcolorfulstrip_instruction_config.yaml \
    --output-dir data/F2longcolorfulstrip/ \
    --split-samples train:1000,test:100 \
    --shuffle
