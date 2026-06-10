#!/usr/bin/env bash
# set -xeuo pipefail 2>/dev/null || set -xeu

## !!!!!!!important!!!!!!
## set the following environment variables on all your nodes
# env_vars:
#   CUDA_DEVICE_MAX_CONNECTIONS: "1"
#   NCCL_NVLS_ENABLE: "0"
#   VLLM_USE_V1: 1
# install mbridge=0.1.13 on all your node with the following command: 
# pip3 install git+https://github.com/ISEEKYAN/mbridge

# SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# [ -f "${SCRIPT_DIR}/env.sh" ] && source "${SCRIPT_DIR}/env.sh"
set -x

ulimit -n 65535

# 当前项目根目录
PROJECT_DIR="$(pwd)"
# exp项目名称
project_name="example_bootcamp"
# 实验名称
current_time=$(date "+%Y%m%d%H%M%S")
experiment_name="example_bootcamp_grpo_Qwen3_sglang_megatron_${current_time}"


worker_gpu=8
worker_count=2
worker_cpu=64
worker_memory_GB=1600

# Trainer parameters
n_gpus_per_node=8
nnodes=$worker_count
logger='["console","tensorboard"]'


image="<CONTAINER_IMAGE>"
# WANDB_MODE=offline

namespace=ailab-llmbr
quota_group=llmbr_gpu # puyullm_gpu llmbr_gpu
# mount=gpfs://gpfs1/<USER>:${USER_STORAGE} 
preemptible=no # yes no

# 容器级别重启
auto_restart=false # false true always;  always表示无论什么原因导致任务退出都重启
restart_policy=never # 重启策略：(choose from 'never', 'onfailure', 'restartjobonfailure')
# Always : 只要 Pod 中的容器终止运行（无论退出代码是什么，0 还是非 0），kubelet（节点上的代理）都会自动重启该容器。
# OnFailure: 只有当 Pod 中的容器以非零退出代码（即失败状态）终止时，kubelet 才会重启该容器。如果容器正常退出（退出代码为 0），则不会重启。只重启失败的pod，而不是整个job。这个比较适合部分拉镜像慢的问题，只重启主节点
# restartjobonfailure 是只要有一个pod失败，就重启整个job。这个比较适合通用的训练断点恢复等任务。
backoff_limit=9999 # 任务失败重试次数

# 仪电推荐的job级别的重启("自愈")
# 失败的就任务停掉重启拉起来一个一模一样的任务。我的理解是和阿里云的重启类似，重新拉起任务重新分配资源。
# 目前自愈可能bug比较多，先别用
# https://iqeubg8au73.feishu.cn/docx/VEyddBrH5oEGlexzOVUcnlTan6x
enable_self_health=false
self_health_count=9999
grace_period_minutes=10 # 自愈介入时间，即获取到告警后，多久开始自愈
termination_grace_period_minutes=3 # 数据回收时间，发送信号-15 到容器，等待回收时间到期后开始重建任务 / 旧任务终止与新任务重启之间的等待时间,用于数据的保存或回收,超时将开始终止旧任务,并基于框架设定的策略拉起新任务

# 模型路径
MODEL_PATH="${MODEL_PATH}"

# 配置文件路径
CONFIG_PATH="${PROJECT_DIR}/internbootcamp/bootcamps/example_bootcamp/configs/"
# 配置文件名
CONFIG_NAME="example_multiturn_w_interaction_grpo"
# 工具配置文件路径
## 远程工具配置文件路径
# TOOL_CONFIG_PATH="internbootcamp/bootcamps/example_bootcamp/configs/example_tool_config_with_server_urls.yaml"
## 本地工具配置文件路径
TOOL_CONFIG_PATH="internbootcamp/bootcamps/example_bootcamp/configs/example_tool_config.yaml"
# 交互配置文件路径
INTERACTION_CONFIG_PATH="internbootcamp/bootcamps/example_bootcamp/configs/example_interaction_config.yaml"

# 数据路径
DATA_TRAIN_FILE_PATH="${PROJECT_DIR}"
# 验证集数据路径
DATA_VAL_FILE_PATH="${PROJECT_DIR}"


# Algorithm parameters
adv_estimator=grpo
use_kl_in_reward=False
kl_coef=0.0
use_kl_loss=False
kl_loss_coef=0.0
kl_loss_type="low_var_kl"
clip_ratio_low=0.2
clip_ratio_high=0.28
clip_ratio_c=10.0

# Data parameters
filter_overlong_prompts=True
max_prompt_length=2048
filter_overlong_prompts_workers=16
truncation="left"
return_raw_chat=True
no_chat_template=False


# FSDP parameters
actor_strategy="fsdp"
fsdp_param_offload=False
fsdp_optimizer_offload=True
fsdp_reshard_after_forward=True
fsdp_forward_prefetch=False

# Rollout parameters
rollout_mode="async" # async，sync
rollout_prompt_length=$max_prompt_length
rollout_response_length=8192
rollout_n=4
gen_tp=4
rollout_name="sglang"
gpu_memory_utilization=0.5
rollout_log_prob_micro_batch_size_per_gpu=8
rollout_log_prob_use_dynamic_bsz=True
enable_chunked_prefill=True
max_num_batched_tokens=$((rollout_prompt_length + rollout_response_length) * 4)
disable_log_stats=True
enforce_eager=False
free_cache_engine=True
nccl_timeout=1200
temperature=1.0
top_p=0.9
top_k=-1
tokenization_sanity_check_mode="ignore_strippable"
soft_reward=True # only for example_bootcamp
# Multi-turn parameters
max_assistant_turns=32
max_user_turns=$((max_assistant_turns * 4))

# Actor parameters
actor_lr=1e-6
lr_warmup_steps=0
weight_decay=0.1
clip_grad=1.0
loss_agg_mode="seq-mean-token-mean"
entropy_coeff=0
enable_gradient_checkpointing=False  # 对于 MoE 模型，梯度检查点可能导致 CheckpointError，需要禁用
use_remove_padding=True
use_fused_kernels=False
actor_ppo_max_token_len=$((rollout_prompt_length + rollout_response_length))

# Training parameters
train_prompt_bsz=16
ppo_epochs=1 # Number of epochs for GRPO updates on one set of sampled trajectories for actor
ppo_mini_batch_size=4 
ppo_micro_batch_size=null # useless when use_dynamic_bsz is True
ppo_micro_batch_size_per_gpu=null # useless when use_dynamic_bsz is True
use_dynamic_bsz=True
total_epochs=15
save_freq=-1
test_freq=10
val_before_train=False
critic_warmup=0
resume_mode="auto"
log_val_generations=10

# Validation parameters
val_top_p=0.7
val_temperature=${temperature}
val_top_k=${top_k}
val_do_sample=True
val_n=1

# Ref parameters
ref_log_prob_micro_batch_size_per_gpu=8
ref_log_prob_use_dynamic_bsz=True
ref_log_prob_max_token_len_per_gpu=$((rollout_prompt_length + rollout_response_length))



# Reward model parameters
reward_manager="naive"
enable_overlong_buffer=False
overlong_buffer_len=$((1024 * 1))
overlong_penalty_factor=1.0

init_command="export PIP_INDEX_URL=https://pypi.org/simple && export PIP_EXTRA_INDEX_URL=https://pypi.org/simple && export PIP_TRUSTED_HOST='pypi.org' && pip install -e $PROJECT_DIR --no-deps && pip install -e $PROJECT_DIR/verl --no-deps"


# 构建训练命令
cmd="train_files=\"['$DATA_TRAIN_FILE_PATH']\"
test_files=\"['$DATA_VAL_FILE_PATH']\"

set -x

export VERL_PPO_LOGGING_LEVEL=DEBUG
export HYDRA_FULL_ERROR=1

python -m verl.trainer.main_ppo \\
    --config-path=\"$CONFIG_PATH\" \\
    --config-name=\"$CONFIG_NAME\" \\
    trainer.default_hdfs_dir=null \\
    trainer.default_local_dir=$PROJECT_DIR/ckpts/$experiment_name \\
    trainer.rollout_data_dir=$PROJECT_DIR/ckpts/$experiment_name/rollout \\
    actor_rollout_ref.actor.checkpoint.save_contents=['model','optimizer','extra'] \\
    actor_rollout_ref.rollout.mode=$rollout_mode \\
    actor_rollout_ref.rollout.agent.default_agent_loop=tool_agent \\
    actor_rollout_ref.rollout.multi_turn.enable=True \\
    actor_rollout_ref.rollout.multi_turn.tool_config_path=$TOOL_CONFIG_PATH \\
    actor_rollout_ref.rollout.multi_turn.interaction_config_path=$INTERACTION_CONFIG_PATH \\
    actor_rollout_ref.rollout.multi_turn.tokenization_sanity_check_mode=$tokenization_sanity_check_mode \\
    actor_rollout_ref.rollout.multi_turn.max_assistant_turns=$max_assistant_turns \\
    actor_rollout_ref.rollout.multi_turn.max_user_turns=$max_user_turns \\
    algorithm.adv_estimator=${adv_estimator} \\
    algorithm.use_kl_in_reward=${use_kl_in_reward} \\
    algorithm.kl_ctrl.kl_coef=${kl_coef} \\
    data.train_files=\"\$train_files\" \\
    data.val_files=\"\$test_files\" \\
    +data.no_chat_template=$no_chat_template \\
    data.train_batch_size=$train_prompt_bsz \\
    data.val_batch_size=1024 \\
    data.truncation=$truncation \\
    data.return_raw_chat=$return_raw_chat \\
    data.filter_overlong_prompts=$filter_overlong_prompts \\
    data.filter_overlong_prompts_workers=$filter_overlong_prompts_workers \\
    data.max_prompt_length=$max_prompt_length \\
    actor_rollout_ref.rollout.prompt_length=$rollout_prompt_length \\
    actor_rollout_ref.rollout.response_length=$rollout_response_length \\
    actor_rollout_ref.model.path=$MODEL_PATH \\
    actor_rollout_ref.model.use_remove_padding=$use_remove_padding \\
    actor_rollout_ref.model.enable_gradient_checkpointing=$enable_gradient_checkpointing \\
    actor_rollout_ref.actor.optim.lr=$actor_lr \\
    actor_rollout_ref.actor.optim.lr_warmup_steps=$lr_warmup_steps \\
    actor_rollout_ref.actor.optim.weight_decay=$weight_decay \\
    actor_rollout_ref.actor.use_fused_kernels=$use_fused_kernels \\
    actor_rollout_ref.actor.ppo_mini_batch_size=$ppo_mini_batch_size \\
    actor_rollout_ref.actor.ppo_micro_batch_size=$ppo_micro_batch_size \\
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=$ppo_micro_batch_size_per_gpu \\
    actor_rollout_ref.actor.use_dynamic_bsz=${use_dynamic_bsz} \\
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=${actor_ppo_max_token_len} \\
    actor_rollout_ref.actor.use_kl_loss=${use_kl_loss} \\
    actor_rollout_ref.actor.kl_loss_coef=${kl_loss_coef} \\
    actor_rollout_ref.actor.kl_loss_type=$kl_loss_type \\
    actor_rollout_ref.actor.strategy=$actor_strategy \\
    actor_rollout_ref.actor.loss_agg_mode=$loss_agg_mode \\
    actor_rollout_ref.actor.entropy_coeff=$entropy_coeff \\
    actor_rollout_ref.actor.clip_ratio_low=${clip_ratio_low} \\
    actor_rollout_ref.actor.clip_ratio_high=${clip_ratio_high} \\
    actor_rollout_ref.actor.clip_ratio_c=${clip_ratio_c} \\
    actor_rollout_ref.actor.grad_clip=$clip_grad \\
    actor_rollout_ref.actor.fsdp_config.param_offload=${fsdp_param_offload} \\
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=${fsdp_optimizer_offload} \\
    actor_rollout_ref.actor.fsdp_config.reshard_after_forward=${fsdp_reshard_after_forward} \\
    actor_rollout_ref.actor.fsdp_config.forward_prefetch=${fsdp_forward_prefetch} \\
    actor_rollout_ref.actor.ppo_epochs=$ppo_epochs \\
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=$rollout_log_prob_micro_batch_size_per_gpu \\
    actor_rollout_ref.rollout.log_prob_use_dynamic_bsz=${rollout_log_prob_use_dynamic_bsz} \\
    actor_rollout_ref.rollout.tensor_model_parallel_size=${gen_tp} \\
    actor_rollout_ref.rollout.disable_log_stats=$disable_log_stats \\
    actor_rollout_ref.rollout.name=$rollout_name \\
    actor_rollout_ref.rollout.max_num_batched_tokens=$max_num_batched_tokens \\
    actor_rollout_ref.rollout.gpu_memory_utilization=$gpu_memory_utilization \\
    actor_rollout_ref.rollout.n=$rollout_n \\
    actor_rollout_ref.rollout.temperature=${temperature} \\
    actor_rollout_ref.rollout.top_p=${top_p} \\
    actor_rollout_ref.rollout.top_k=${top_k} \\
    actor_rollout_ref.rollout.enable_chunked_prefill=$enable_chunked_prefill \\
    actor_rollout_ref.rollout.enforce_eager=$enforce_eager \\
    actor_rollout_ref.rollout.free_cache_engine=$free_cache_engine \\
    actor_rollout_ref.rollout.val_kwargs.temperature=${val_temperature} \\
    actor_rollout_ref.rollout.val_kwargs.top_p=${val_top_p} \\
    actor_rollout_ref.rollout.val_kwargs.top_k=${val_top_k} \\
    actor_rollout_ref.rollout.val_kwargs.do_sample=$val_do_sample \\
    actor_rollout_ref.rollout.val_kwargs.n=$val_n \\
    actor_rollout_ref.nccl_timeout=$nccl_timeout \\
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=$ref_log_prob_micro_batch_size_per_gpu \\
    actor_rollout_ref.ref.log_prob_use_dynamic_bsz=${ref_log_prob_use_dynamic_bsz} \\
    actor_rollout_ref.ref.log_prob_max_token_len_per_gpu=${ref_log_prob_max_token_len_per_gpu} \\
    actor_rollout_ref.ref.fsdp_config.param_offload=${fsdp_param_offload} \\
    reward_model.reward_manager=$reward_manager \\
    +reward_model.reward_kwargs.soft_reward=${soft_reward} \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.enable=${enable_overlong_buffer} \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.len=${overlong_buffer_len} \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.penalty_factor=${overlong_penalty_factor} \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.log=False \\
    +reward_model.reward_kwargs.max_resp_len=${rollout_response_length} \\
    trainer.critic_warmup=$critic_warmup \\
    trainer.logger=$logger \\
    trainer.project_name=$project_name \\
    trainer.experiment_name=$experiment_name \\
    trainer.n_gpus_per_node=$n_gpus_per_node \\
    trainer.nnodes=$nnodes \\
    trainer.save_freq=$save_freq \\
    trainer.test_freq=$test_freq \\
    trainer.val_before_train=$val_before_train \\
    trainer.total_epochs=$total_epochs \\
    trainer.resume_mode=$resume_mode \\
    trainer.log_val_generations=$log_val_generations \$@"



echo "$cmd" > ./training_configs/$experiment_name.sh

bash_command="cd $PROJECT_DIR && $init_command && python examples/start_train_yidian.py 'sh ./training_configs/$experiment_name.sh' $worker_count"

rjob submit -e DISTRIBUTED_JOB=true \
    --namespace=$namespace  \
    --image=$image \
    --host-network=true --name $experiment_name -P $worker_count --gpu $worker_gpu --cpu $worker_cpu --memory $((worker_memory_GB * 1024)) --charged-group $quota_group \
    --private-machine='group' \
    --gang-start=true \
    --mount=gpfs://gpfs1/<USER>:${USER_STORAGE} \
    --mount=gpfs://gpfs1/large-model-center-share-weights:${MODEL_STORAGE} \
    --mount=gpfs://<GPFS_WORKSPACE>:${SHARED_WORKSPACE} \
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
    -- bash -ecx "$bash_command"


