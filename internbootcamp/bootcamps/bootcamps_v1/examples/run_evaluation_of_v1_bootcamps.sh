
# 评测数据集路径
DATASET_PATH="data/filtered_v1_bootcamps/v1_bootcamps_test-mini.jsonl"
# 评测输出目录
OUTPUT_DIR="data/eval_output/"
# API 密钥
## 使用硅流API
# API_KEY="${API_KEY}"
## 使用volcengine API
API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZ3VvcWlwZW5nIiwiZXhwIjoxNzk4NzYxNjAwfQ.9An25TNKrhC6K8OIluuSjFGCBEtrr6414vmTqC5q6FQ"
# API 地址
API_URL="http://100.96.35.28:15539/v1"
# API 模型名称
API_MODEL="qwen3-30b-step-150"
# Bootcamp 配置文件路径
BOOTCAMP_REGISTRY="internbootcamp/examples/bootcamp_registry/bootcamp_registry_of_filtered_v1_bootcamps.jsonl"
# 断点重试模式：指定要恢复的结果文件路径(.jsonl)
# RESUME_FROM_RESULT_PATH="data/eval_output/qwen3-30b-sr100-step-200/eval_results_20251014023510.jsonl"

# 最大对话轮数
MAX_TOOL_TURNS_PER_INTERACTION=20
MAX_INTERACTION_TURNS=5
# 最大并发数
MAX_CONCURRENT=512

# 执行评测命令
python -m internbootcamp.utils.run_evaluation \
    --dataset-path "$DATASET_PATH" \
    --output-dir "$OUTPUT_DIR" \
    --api-key "$API_KEY" \
    --api-url "$API_URL" \
    --api-model "$API_MODEL" \
    --bootcamp-registry "$BOOTCAMP_REGISTRY" \
    --max-tool-turns-per-interaction $MAX_TOOL_TURNS_PER_INTERACTION \
    --max-interaction-turns $MAX_INTERACTION_TURNS \
    --max-concurrent $MAX_CONCURRENT \
    --tokenizer-path "${MODEL_PATH}" \
    --resume-from-result-path "$RESUME_FROM_RESULT_PATH" \
    --api-extra-params "max_tokens:32768" \
    --verbose \
    # --dry-run