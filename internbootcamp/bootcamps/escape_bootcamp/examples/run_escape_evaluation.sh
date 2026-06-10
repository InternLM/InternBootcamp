declare -A api_config1=(
    [key]="${API_KEY}"
    [url]="https://api.boyuerichdata.opensphereai.com/v1"
    [model]="gemini-3.1-pro-preview"
)
declare -A api_config2=(
    [key]="${API_KEY}"
    [url]="https://api.boyuerichdata.opensphereai.com/v1"
    [model]="gemini-3.1-pro-preview-thinking"
)
declare -A api_config3=(
    [key]="${API_KEY}"
    [url]="https://api.boyuerichdata.opensphereai.com/v1"
    [model]="Qwen/Qwen3-VL-235B-A22B-Thinking"
)
declare -A api_config4=(
    [key]="${API_KEY}"
    [url]="https://api.boyuerichdata.opensphereai.com/v1"
    [model]="Qwen/Qwen3-VL-235B-A22B-Instruct"
)
declare -A api_config5=(
    [key]="${API_KEY}"
    [url]="https://api.boyuerichdata.opensphereai.com/v1"
    [model]="Qwen/Qwen3-VL-30B-A3B-Instruct"
)
declare -A api_config6=(
    [key]="${API_KEY}"
    [url]="https://api.boyuerichdata.opensphereai.com/v1"
    [model]="Qwen/Qwen3-VL-8B-Instruct"
)
declare -A api_config7=(
    [key]="${API_KEY}"
    [url]="https://chat.intern-ai.org.cn/api/v1/"
    [model]="intern-s1"
)
declare -A api_config8=(
    [key]="${API_KEY}"
    [url]="http://100.102.199.158:21036/v1"
    [model]="kimi-k2.5"
)
declare -A api_config9=(
    [key]="${API_KEY}"
    [url]="http://100.102.199.158:21036/v1"
    [model]="kimi-k2.5"
    [enable_thinking]="True"
)
declare -A api_config10=(
    [key]="${API_KEY}"
    [url]="http://100.102.199.158:21036/v1"
    [model]="qwen3.5-397b-a17b"
)
declare -A api_config11=(
    [key]="${API_KEY}"
    [url]="http://100.102.199.158:21036/v1"
    [model]="qwen3.5-397b-a17b"
    [enable_thinking]="True"
)
# declare -A api_config12=(
#     [key]="${API_KEY}"
#     [url]="https://api.boyuerichdata.opensphereai.com/v1"
#     [model]="qwen3.5-397b-a17b"
# )
declare -A api_config13=(
    [key]="${API_KEY}"
    [url]="https://api.boyuerichdata.opensphereai.com/v1"
    [model]="kimi-k2.5"
    [temperature]=1
)
# declare -A api_config14=(
#     [key]="${API_KEY}"
#     [url]="https://api.boyuerichdata.opensphereai.com/v1"
#     [model]="kimi-k2.5"
#     [enable_thinking]="True"
#     [temperature]=1
# )
# declare -A api_config15=(
#     [key]="${API_KEY}"
#     [url]="https://api.boyuerichdata.opensphereai.com/v1"
#     [model]="claude-opus-4-6"
# )


# declare -A api_config5=(
#     [key]="${API_KEY}"
#     [url]="https://api.boyuerichdata.opensphereai.com/v1"
#     [model]="qwen3-8b"
#     [enable_thinking]="True"
# )

start=13; end=13
# -----------------------------------------------------------------------------------------------------------------------

# 评测数据集路径
# DATASET_PATH="internbootcamp/bootcamps/escape_bootcamp/data/escape_bootcamp/escape_20260116211254_train_1.jsonl"
DATASET_PATH="internbootcamp/bootcamps/escape_bootcamp/data/escape_bootcamp/escape_20260116211254_test.jsonl"
# 评测输出目录
OUTPUT_DIR="internbootcamp/bootcamps/escape_bootcamp/data/eval_output/"
# 评测器类
EVALUATOR_CLASS="internbootcamp.src.base_evaluator.BaseEvaluator"
# 奖励计算器类
REWARD_CALCULATOR_CLASS="internbootcamp.bootcamps.escape_bootcamp.escape_reward_calculator.EscapeRewardCalculator"
# 工具配置文件路径
## mcp tool
TOOL_CONFIG="internbootcamp/bootcamps/escape_bootcamp/configs/escape_tool_config_with_server_urls.yaml"
## tool
# TOOL_CONFIG="internbootcamp/bootcamps/example_bootcamp/configs/example_tool_config.yaml" 
# 交互配置文件路径
INTERACTION_CONFIG="internbootcamp/bootcamps/escape_bootcamp/configs/escape_interaction_config.yaml"

# 最大LLM轮数
MAX_ASSISTANT_TURNS=50
MAX_USER_TURNS=50
# 最大并发数
MAX_CONCURRENT=8

TOKENIZER_PATH="${MODEL_PATH}"

# 执行评测命令
for config_num in $(seq "$start" "$end"); do
    config_name="api_config$config_num"
    declare -n config=$config_name
    
    API_KEY="${config[key]}"
    API_URL="${config[url]}"
    API_MODEL="${config[model]}"
    if [[ -v "config[temperature]" ]]; then
        API_TEMP=${config[temperature]}
    else
        API_TEMP=0.7
    fi
    if [[ -v "config[enable_thinking]" ]]; then
        if [[ "${config[enable_thinking]}" == "True" ]]; then
            PARAMS='{"temperature":'"$API_TEMP"',"max_completion_tokens":32768,"extra_body":{"enable_thinking":true}}'
        else
            PARAMS='{"temperature":'"$API_TEMP"',"max_completion_tokens":32768,"extra_body":{"enable_thinking":false}}'
        fi
    else
        PARAMS='{"temperature":'"$API_TEMP"',"max_completion_tokens":32768}'
    fi

    # 设置代理
    if [[ "$API_URL" == *"boyue"* ]] || [[ "$API_URL" == *"intern"* ]]; then
        export http_proxy=http://<PROXY_USER>:<PROXY_PASSWORD>@<PROXY_HOST>:23128/
        export https_proxy=http://<PROXY_USER>:<PROXY_PASSWORD>@<PROXY_HOST>:23128/
        export HTTP_PROXY=http://<PROXY_USER>:<PROXY_PASSWORD>@<PROXY_HOST>:23128/
        export HTTPS_PROXY=http://<PROXY_USER>:<PROXY_PASSWORD>@<PROXY_HOST>:23128/
    else
        unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    fi

    python -m internbootcamp.utils.run_evaluation \
        --dataset-path "$DATASET_PATH" \
        --output-dir "$OUTPUT_DIR" \
        --api-key "$API_KEY" \
        --api-url "$API_URL" \
        --api-model "$API_MODEL" \
        --evaluator-class "$EVALUATOR_CLASS" \
        --reward-calculator-class "$REWARD_CALCULATOR_CLASS" \
        --tool-config "$TOOL_CONFIG" \
        --interaction-config "$INTERACTION_CONFIG" \
        --max-assistant-turns $MAX_ASSISTANT_TURNS \
        --max-user-turns $MAX_USER_TURNS \
        --max-concurrent $MAX_CONCURRENT \
        --api-extra-params $PARAMS \
        --verify-correction-kwargs '{"soft_reward": true}' \
        --tokenizer-path $TOKENIZER_PATH \
        --verbose > "logs/$(date +%Y%m%d_%H%M%S)_$RANDOM.log" 2>&1
        # --resume-from-result-path "internbootcamp/bootcamps/escape_bootcamp/data/eval_output/intern-s1/eval_results_20260120142313_682533.jsonl"
        # --dry-run \
        # --api-extra-params '{"temperature":0.7, "max_completion_tokens":65536, "extra_body": {"enable_thinking": true}}' \
done
