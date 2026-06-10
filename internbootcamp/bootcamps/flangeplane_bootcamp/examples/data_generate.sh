#! /bin/bash

NUM_RUNS=10

for ((i=1; i<=NUM_RUNS; i++))
do
    echo "正在启动第 $i 个任务..."

    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

    # 构建带有时间戳的日志文件名
    LOG_FILE="internbootcamp/bootcamps/flangeplane_bootcamp/data/flangeplane_bootcamp/run_${i}_${TIMESTAMP}.log"
        
    python -m internbootcamp.utils.data_generation \
        --instruction-config internbootcamp/bootcamps/flangeplane_bootcamp/configs/flangeplane_instruction_config.yaml \
        --output-dir internbootcamp/bootcamps/flangeplane_bootcamp/data/flangeplane_bootcamp/ \
        --split-samples train:10000,test:0 \
        --shuffle \
        > "$LOG_FILE" 2>&1 &

    echo $!
    sleep 5
done

wait
