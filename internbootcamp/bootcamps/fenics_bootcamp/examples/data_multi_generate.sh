#!/bin/bash
#!/bin/bash
set -e

# 从项目根目录运行
cd "$(dirname "$0")"/../../../..

NUM_RUNS=16

for ((i=1; i<=NUM_RUNS; i++))
do
    echo "正在启动第 $i 个任务..."

    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

    # 构建带有时间戳的日志文件名
    LOG_FILE="internbootcamp/bootcamps/fenics_bootcamp/data/fenics_bootcamp/run_${i}_${TIMESTAMP}.log"

    python -m internbootcamp.utils.data_generation \
        --instruction-config internbootcamp/bootcamps/fenics_bootcamp/configs/fenics_instruction_config.yaml \
        --output-dir internbootcamp/bootcamps/fenics_bootcamp/data/fenics_bootcamp/ \
        --split-samples train:6250,test:0 \
        --shuffle \
        > "$LOG_FILE" 2>&1 &

    echo $!
    sleep 5
done

wait