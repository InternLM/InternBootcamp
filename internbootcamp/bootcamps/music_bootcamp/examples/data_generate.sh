#!/bin/bash

python -m internbootcamp.utils.data_generation \
    --instruction-config internbootcamp/bootcamps/music_bootcamp/configs/music_instruction_config.yaml \
    --output-dir internbootcamp/bootcamps/music_bootcamp/data/music_bootcamp/ \
    --split-samples train:0,test:10 \
    --shuffle 
