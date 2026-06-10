#!/bin/bash

NUM_RUNS=50

for ((i=1; i<=NUM_RUNS; i++))
do
    echo "正在启动第 $i 个任务..."

    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

    # 构建带有时间戳的日志文件名
    LOG_FILE="internbootcamp/bootcamps/battery_bootcamp/data/battery_bootcamp/run_${i}_${TIMESTAMP}.log"


    python -m internbootcamp.utils.data_generation \
        --instruction-config internbootcamp/bootcamps/battery_bootcamp/configs/battery_instruction_config.yaml \
        --output-dir internbootcamp/bootcamps/battery_bootcamp/data/battery_bootcamp/ \
        --split-samples train:760,test:0 \
        --shuffle \
        --global-config-overrides '{"gen_parquet": false}' \
        > "$LOG_FILE" 2>&1 &

    echo $!
    sleep 5
done

wait
