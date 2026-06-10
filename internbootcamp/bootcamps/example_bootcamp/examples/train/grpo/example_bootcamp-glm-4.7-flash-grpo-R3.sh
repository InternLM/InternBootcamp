#!/usr/bin/env bash

# ============================================================================
# 项目基本信息
# ============================================================================
project_name="example_bootcamp"
experiment_name="example_bootcamp-glm-4.7-flash-grpo-R3"
internbootcamp_path="${PROJECT_DIR}"
verl_path="${PROJECT_DIR}"
verl_data_path="${CACHE_DIR}"

cd $internbootcamp_path

echo "========================================="
echo "实验名称: $experiment_name"
echo "========================================="

# ============================================================================
# 集群资源配置
# ============================================================================
worker_gpu=8
worker_cpu=32
worker_count=1
worker_memory_GB=1000

# ============================================================================
# 集群调度配置
# ============================================================================
image="<CONTAINER_IMAGE>"
namespace="ailab-llmbr"
quota_group="llmbr_gpu"
preemptible=no
auto_restart=false
restart_policy=never
backoff_limit=9999
grace_period_minutes=10
enable_self_health=false
self_health_count=9999
termination_grace_period_minutes=3

# ============================================================================
# 模型和配置路径
# ============================================================================
actor_model="${MODEL_PATH}"
CONFIG_PATH="${internbootcamp_path}/internbootcamp/bootcamps/example_bootcamp/configs"
CONFIG_NAME="example_multiturn_w_tool_grpo.yaml"
TOOL_CONFIG_PATH="${internbootcamp_path}/internbootcamp/bootcamps/example_bootcamp/configs/example_tool_config_with_server_urls.yaml"
INTERACTION_CONFIG_PATH="${internbootcamp_path}/internbootcamp/bootcamps/example_bootcamp/configs/example_interaction_config.yaml"

# ============================================================================
# 数据路径 (统一加上单引号，以便之后使用多个文件)
# ============================================================================
DATA_TRAIN_FILE_PATH="${internbootcamp_path}/internbootcamp/bootcamps/example_bootcamp/data/example_arithmetic/example_20260129125310_train.parquet"
DATA_VAL_FILE_PATH="${internbootcamp_path}/internbootcamp/bootcamps/example_bootcamp/data/example_arithmetic/example_20260128195352_test.parquet"

# ============================================================================
# 训练批次和序列长度配置
# ============================================================================
train_batch_size=8
# ppo_micro_batch_size=16 #disabled when using dynamic batchsize
# rollout_n=8
total_epochs=1
save_freq=5
test_freq=1e+10
balance_batch=False

# ============================================================================
# PPO/算法参数
# ============================================================================
use_kl_in_reward=False
use_kl_loss=False
kl_coef=0.0
kl_loss_coef=0.001
clip_ratio_low=0.2
clip_ratio_high=0.28
loss_agg_mode="seq-mean-token-mean"
use_dynamic_bsz=True

# ============================================================================
# Rollout 配置
# ============================================================================
enable_overlong_buffer=False
filter_overlong_prompts=False
filter_overlong_prompts_workers=16
max_num_batched_tokens=$((1024 * 256))
rollout_tensor_model_parallel_size=1
rollout_gpu_memory_utilization=0.65


# ============================================================================
# Actor 配置
# ============================================================================
actor_ulysses_sequence_parallel_size=1

# ============================================================================
# Routing Replay 配置
# ============================================================================

# R2: enable routing replay
# R3: enable rollout routing replay
# If enabling R3, please set actor_rollout_ref.rollout.enable_rollout_routing_replay=True 
# R3 example is based on vllm related pr https://github.com/vllm-project/vllm/pull/5322

ROUTING_REPLAY_MODE="R3"
enable_rollout_routing_replay=True


# ============================================================================
# GRPO/算法参数
# ============================================================================
rollout_n=8 # 普通 GRPO 的 rollout 采样次数
max_assistant_turns=16
max_response_length=4096 # 单次响应的最大长度
data_max_prompt_length=2048
max_prompt_length=$((data_max_prompt_length + max_response_length)) # 包含历史 context
max_token_len=$((max_prompt_length + max_response_length)) # 如果rollout显存不够这个值最低是$((max_prompt_length + max_response_length))，否则也许可以大一点使bsz被有效利用？
ppo_mini_batch_size=$train_batch_size # 普通 GRPO 的 mini_batch_size
default_agent_loop=tool_agent # 使用标准的 tool_agent

# ============================================================================
# 奖励模型配置 (example_bootcamp 使用 bootcamp reward_manager)
# ============================================================================
reward_manager=naive
reward_eval_mode=False
soft_reward=True
overlong_penalty_factor=0.0

init_cmd="export PIP_TIMEOUT=600 && export PIP_INDEX_URL='https://pypi.org/simple' && export PIP_EXTRA_INDEX_URL='https://pypi.org/simple' && export PIP_TRUSTED_HOST='pypi.org' && pip install  $internbootcamp_path  && pip install  $verl_path --no-deps"

mkdir -p ./training_configs
mkdir -p $internbootcamp_path/outputs
chmod 755 ./training_configs

# ============================================================================
# 生成训练配置脚本 (使用 cat <<EOF 避免引号嵌套问题)
# ============================================================================
cat > ./training_configs/$experiment_name.sh <<EOF
export VERL_PPO_LOGGING_LEVEL=DEBUG
export HYDRA_FULL_ERROR=1
train_files="[$DATA_TRAIN_FILE_PATH]"
test_files="[$DATA_VAL_FILE_PATH]"
set -x
chmod -R 777 $internbootcamp_path/outputs
python -m verl.trainer.main_ppo \\
    --config-name="$CONFIG_NAME" \\
    --config-path="$CONFIG_PATH" \\
    actor_rollout_ref.actor.clip_ratio_high=$clip_ratio_high \\
    actor_rollout_ref.actor.clip_ratio_low=$clip_ratio_low \\
    actor_rollout_ref.actor.entropy_checkpointing=True \\
    actor_rollout_ref.actor.entropy_from_logits_with_chunking=True \\
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \\
    actor_rollout_ref.actor.fsdp_config.param_offload=True \\
    actor_rollout_ref.actor.fsdp_config.reshard_after_forward=True \\
    actor_rollout_ref.actor.grad_clip=1.0 \\
    actor_rollout_ref.actor.kl_loss_coef=$kl_loss_coef \\
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \\
    actor_rollout_ref.actor.loss_agg_mode=$loss_agg_mode \\
    actor_rollout_ref.actor.optim.lr=1e-6 \\
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=$max_token_len \\
    actor_rollout_ref.actor.ppo_mini_batch_size=$ppo_mini_batch_size \\
    actor_rollout_ref.actor.ulysses_sequence_parallel_size=$actor_ulysses_sequence_parallel_size \\
    actor_rollout_ref.actor.use_dynamic_bsz=$use_dynamic_bsz \\
    actor_rollout_ref.actor.use_kl_loss=$use_kl_loss \\
    actor_rollout_ref.actor.router_replay.mode=${ROUTING_REPLAY_MODE} \\
    actor_rollout_ref.model.enable_activation_offload=True \\
    actor_rollout_ref.model.enable_gradient_checkpointing=True \\
    actor_rollout_ref.model.path=$actor_model \\
    actor_rollout_ref.model.use_remove_padding=True \\
    actor_rollout_ref.ref.fsdp_config.param_offload=True \\
    actor_rollout_ref.ref.log_prob_max_token_len_per_gpu=$max_token_len \\
    actor_rollout_ref.ref.log_prob_use_dynamic_bsz=$use_dynamic_bsz \\
    actor_rollout_ref.rollout.enable_rollout_routing_replay=$enable_rollout_routing_replay \\
    actor_rollout_ref.rollout.agent.default_agent_loop=$default_agent_loop \\
    actor_rollout_ref.rollout.disable_log_stats=True \\
    actor_rollout_ref.rollout.enable_chunked_prefill=True \\
    actor_rollout_ref.rollout.enforce_eager=False \\
    actor_rollout_ref.rollout.free_cache_engine=True \\
    actor_rollout_ref.rollout.gpu_memory_utilization=$rollout_gpu_memory_utilization \\
    actor_rollout_ref.rollout.log_prob_max_token_len_per_gpu=$max_token_len \\
    actor_rollout_ref.rollout.max_num_batched_tokens=$max_num_batched_tokens \\
    actor_rollout_ref.rollout.mode="async" \\
    actor_rollout_ref.rollout.multi_turn.max_assistant_turns=$max_assistant_turns \\
    actor_rollout_ref.rollout.multi_turn.tokenization_sanity_check_mode=ignore_strippable \\
    actor_rollout_ref.rollout.multi_turn.tool_config_path=$TOOL_CONFIG_PATH \\
    actor_rollout_ref.rollout.multi_turn.interaction_config_path=$INTERACTION_CONFIG_PATH \\
    actor_rollout_ref.rollout.n=$rollout_n \\
    actor_rollout_ref.rollout.name=sglang \\
    actor_rollout_ref.rollout.response_length=$max_response_length \\
    actor_rollout_ref.rollout.temperature=1 \\
    actor_rollout_ref.rollout.tensor_model_parallel_size=$rollout_tensor_model_parallel_size \\
    actor_rollout_ref.rollout.top_k=-1 \\
    actor_rollout_ref.rollout.top_p=0.9 \\
    algorithm.adv_estimator=grpo \\
    algorithm.kl_ctrl.kl_coef=$kl_coef \\
    algorithm.use_kl_in_reward=$use_kl_in_reward \\
    reward_model.reward_manager=$reward_manager \\
    +reward_model.reward_kwargs.soft_reward=$soft_reward \\
    +reward_model.reward_kwargs.eval_mode=$reward_eval_mode \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.enable=${enable_overlong_buffer} \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.len=${max_response_length} \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.penalty_factor=${overlong_penalty_factor} \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.log=False \\
    +reward_model.reward_kwargs.max_resp_len=${max_response_length} \\
    data.filter_overlong_prompts=$filter_overlong_prompts \\
    data.filter_overlong_prompts_workers=$filter_overlong_prompts_workers \\
    data.max_prompt_length=$max_prompt_length \\
    data.max_response_length=$max_response_length \\
    +data.no_chat_template=False \\
    data.return_raw_chat=True \\
    data.train_batch_size=$train_batch_size \\
    data.train_files="\$train_files" \\
    data.truncation=left \\
    data.val_batch_size=1024 \\
    data.val_files="\$test_files" \\
    trainer.balance_batch=$balance_batch \\
    trainer.critic_warmup=0 \\
    trainer.default_hdfs_dir=null \\
    trainer.default_local_dir=$verl_data_path/ckpts/$experiment_name \\
    trainer.experiment_name=$experiment_name \\
    trainer.logger=['console','tensorboard'] \\
    trainer.n_gpus_per_node=$worker_gpu \\
    trainer.nnodes=$worker_count \\
    trainer.project_name=$project_name \\
    trainer.resume_mode=auto_scan \\
    trainer.rollout_data_dir=$verl_data_path/ckpts/$experiment_name/rollout \\
    trainer.save_freq=$save_freq \\
    trainer.test_freq=$test_freq \\
    trainer.total_epochs=$total_epochs \\
    trainer.val_before_train=False \$@
EOF

chmod 755 ./training_configs/$experiment_name.sh

# ============================================================================
# 提交训练任务
# ============================================================================
bash_command="cd $internbootcamp_path && python examples/start_train_yidian.py 'sh ./training_configs/$experiment_name.sh' $worker_count"

rjob submit -e DISTRIBUTED_JOB=true \
    --image=$image \
    --namespace=$namespace --charged-group $quota_group \
    --host-network=true --name $experiment_name -P $worker_count --gpu $worker_gpu --cpu $worker_cpu --memory $((worker_memory_GB * 1024)) \
    --private-machine='group' \
    --gang-start=true \
    --mount=gpfs://gpfs1/<USER>:${USER_STORAGE} \
    --mount=gpfs://<GPFS_WORKSPACE>:${SHARED_WORKSPACE} \
    --mount=gpfs://gpfs2/dtco-share:${CACHE_STORAGE} \
    --custom-resources rdma/mlnx_shared=8 \
    --custom-resources mellanox.com/mlnx_rdma=1 \
    --auto-restart=$auto_restart \
    --preemptible=$preemptible \
    --restart-policy=$restart_policy \
    --backoff_limit=$backoff_limit \
    --enable-self-health=$enable_self_health \
    --self-health-count=$self_health_count \
    --grace-period-minutes=$grace_period_minutes \
    --termination-grace-period-minutes=$termination_grace_period_minutes \
    --priority=9 \
    -- bash -ecx "$init_cmd && $bash_command"
