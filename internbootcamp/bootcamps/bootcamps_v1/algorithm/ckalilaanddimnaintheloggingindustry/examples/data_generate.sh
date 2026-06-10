#!/bin/bash

# Ckalilaanddimnaintheloggingindustry数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/ckalilaanddimnaintheloggingindustry/configs/Ckalilaanddimnaintheloggingindustry_instruction_config.yaml \
    --output-dir data/Ckalilaanddimnaintheloggingindustry/ \
    --split-samples train:1000,test:100 \
    --shuffle
