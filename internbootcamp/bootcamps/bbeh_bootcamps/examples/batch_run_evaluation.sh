
# 评测数据集路径
DATASET_PATH="internbootcamp/bootcamps/bbeh_bootcamps/data/gen/20251127134058_test.jsonl"
# 评测输出目录
OUTPUT_DIR="internbootcamp/bootcamps/bbeh_bootcamps/data/eval_outputs"
# API 密钥
## 使用硅流API
# API_KEY="${API_KEY}"
## 使用volcengine API
API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZ3VvcWlwZW5nIiwiZXhwIjoxNzk4NzYxNjAwfQ.9An25TNKrhC6K8OIluuSjFGCBEtrr6414vmTqC5q6FQ"
# API 地址
API_URL="http://100.103.25.14:21003/v1"
# API 模型名称
API_MODEL="qwen3-8b-bbeh-1126-s400"
# Bootcamp 配置文件路径
BOOTCAMP_REGISTRY="internbootcamp/bootcamps/bbeh_bootcamps/configs/bbeh_bootcamps_registry.jsonl"
# 断点重试模式：指定要恢复的结果文件路径(.jsonl)
# RESUME_FROM_RESULT_PATH="internbootcamp/bootcamps/bbeh_bootcamps/data/eval_outputs/qwen3-235b-thinking-2507/eval_results_20251117230742.jsonl"

# 最大对话轮数
MAX_ASSISTANT_TURNS=1
MAX_USER_TURNS=1
# 最大并发数
MAX_CONCURRENT=128

# 执行评测命令
python -m internbootcamp.utils.run_evaluation \
    --dataset-path "$DATASET_PATH" \
    --output-dir "$OUTPUT_DIR" \
    --api-key "$API_KEY" \
    --api-url "$API_URL" \
    --api-model "$API_MODEL" \
    --bootcamp-registry "$BOOTCAMP_REGISTRY" \
    --max-assistant-turns "${MAX_ASSISTANT_TURNS}" \
    --max-user-turns "${MAX_USER_TURNS}" \
    --max-concurrent "${MAX_CONCURRENT}" \
    --tokenizer-path "${MODEL_PATH}" \
    --resume-from-result-path "$RESUME_FROM_RESULT_PATH" \
    --api-extra-params '{"temperature":0.6,"max_completion_tokens":16384}' \
    --best-of-n 8 \
    --verbose \
    # --dry-run