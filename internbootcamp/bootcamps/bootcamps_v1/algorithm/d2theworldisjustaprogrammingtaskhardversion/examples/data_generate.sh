#!/bin/bash

# D2theworldisjustaprogrammingtaskhardversion数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/algorithm/d2theworldisjustaprogrammingtaskhardversion/configs/D2theworldisjustaprogrammingtaskhardversion_instruction_config.yaml \
    --output-dir data/D2theworldisjustaprogrammingtaskhardversion/ \
    --split-samples train:1000,test:100 \
    --shuffle
