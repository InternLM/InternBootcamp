
# 评测数据集路径
DATASET_PATH="internbootcamp/bootcamps/example_bootcamp/data/example_arithmetic/example_20260210143614_test.jsonl"
# 评测输出目录
OUTPUT_DIR="internbootcamp/bootcamps/example_bootcamp/data/eval_output/"
# API 密钥
API_KEY="${API_KEY}"
# API 地址
API_URL="http://100.102.199.158:21036/v1"
# API 模型名称
API_MODEL="qwen3-235b-instruct-2507"
# 评测器类
EVALUATOR_CLASS="internbootcamp.src.base_evaluator.BaseEvaluator"
# 奖励计算器类
REWARD_CONFIG="internbootcamp/bootcamps/example_bootcamp/configs/example_reward_config.yaml"
# 工具配置文件路径
## mcp tool
TOOL_CONFIG="internbootcamp/bootcamps/example_bootcamp/configs/example_tool_config.yaml"
## tool
# TOOL_CONFIG="internbootcamp/bootcamps/example_bootcamp/configs/example_tool_config.yaml" 
# 交互配置文件路径
INTERACTION_CONFIG="internbootcamp/bootcamps/example_bootcamp/configs/example_interaction_config.yaml"

# RESUME="internbootcamp/bootcamps/example_bootcamp/data/eval_output/deepseekv3-1-terminus/eval_results_20251022134402.jsonl"
    # --resume-from-result-path $RESUME \
# 最大LLM轮数
MAX_ASSISTANT_TURNS=32
MAX_USER_TURNS=$MAX_ASSISTANT_TURNS
# 最大并发数
MAX_ASSISTANT_CONCURRENT=256
MAX_USER_CONCURRENT=256

TOKENIZER_PATH="${MODEL_PATH}"

# 执行评测命令
python -m internbootcamp.utils.run_evaluation \
    --dataset-path "$DATASET_PATH" \
    --output-dir "$OUTPUT_DIR" \
    --api-key "$API_KEY" \
    --api-url "$API_URL" \
    --api-model "$API_MODEL" \
    --evaluator-class "$EVALUATOR_CLASS" \
    --reward-config "$REWARD_CONFIG" \
    --tool-config "$TOOL_CONFIG" \
    --interaction-config "$INTERACTION_CONFIG" \
    --max-assistant-turns $MAX_ASSISTANT_TURNS \
    --max-user-turns $MAX_USER_TURNS \
    --max-assistant-concurrent $MAX_ASSISTANT_CONCURRENT \
    --max-user-concurrent $MAX_USER_CONCURRENT \
    --api-extra-params '{"temperature":0.7,"max_completion_tokens":32768, "extra_body": {"chat_template_kwargs": {"enable_thinking": False}}}' \
    --verify-correction-kwargs '{"soft_reward": true}' \
    --tokenizer-path $TOKENIZER_PATH \
    --verbose 


# --dry-run \
# --api-extra-params '{"temperature":0.7, "max_completion_tokens":65536, "extra_body": {"enable_thinking": true}}' \