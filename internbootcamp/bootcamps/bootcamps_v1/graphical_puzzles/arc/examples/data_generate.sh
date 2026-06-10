#!/bin/bash

# Arc数据生成脚本

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/arc/configs/arc_instruction_config.yaml \
    --output-dir data/arc/ \
    --tool-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/arc/configs/arc_tool_config.yaml \
    --interaction-config internbootcamp/bootcamps/bootcamps_v1/graphical_puzzles/arc/configs/arc_interaction_config.yaml \
    --split-samples train:1000,test:16 \
    --shuffle
