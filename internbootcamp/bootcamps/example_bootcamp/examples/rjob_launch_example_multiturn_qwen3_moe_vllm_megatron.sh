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

# 任务提交参数设置（原dlc_lanuch.sh内容）
project_name=ExampleBootcamp
current_time=$(date "+%Y%m%d%H%M%S")
experiment_name="examplebootcamp-grpo-Qwen3-${current_time}"
verl_path="${PROJECT_DIR}"
verl_data_path="${USER_STORAGE}/user/<USER>/verl-cache"
cd $verl_path
worker_gpu=8
worker_count=8
worker_cpu=64
image="<CONTAINER_IMAGE>"
# WANDB_MODE=offline
WANDB_API_KEY="350272d1b727788703b1f5d46518d3c1f41b274f"
worker_memory_GB=1600
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

# MODEL_PATH=${MODEL_PATH}
MODEL_PATH=${MODEL_PATH}
# MODEL_PATH=${MODEL_PATH}
# MODEL_PATH=${PROJECT_DIR}
# MODEL_PATH=${PROJECT_DIR}
# 7B qwen必须tp4
CONFIG_PATH="${verl_path}/verl/trainer/config/"
# 配置文件名
CONFIG_NAME="ppo_megatron_trainer.yaml"  
# 工具配置文件路径
## 远程工具配置文件路径
TOOL_CONFIG_PATH="${verl_path}/internbootcamp/bootcamps/example_bootcamp/configs/example_tool_config_with_server_urls.yaml"  
DATA_TRAIN_FILE_PATH="${PROJECT_DIR}"  # 训练集数据路径
# 验证集数据路径
DATA_VAL_FILE_PATH="${PROJECT_DIR}"  
filter_overlong_prompts=True




adv_estimator=grpo

use_kl_in_reward=False
kl_coef=0.0
use_kl_loss=False
kl_loss_coef=0.001

clip_ratio_low=0.2
clip_ratio_high=0.28

max_prompt_length=$((1024 * 2))
max_response_length=$((1204 * 8))
enable_overlong_buffer=True
overlong_buffer_len=$((1024 * 1))
overlong_penalty_factor=1.0

loss_agg_mode="seq-mean-token-mean"

train_prompt_bsz=32
n_resp_per_prompt=8
train_prompt_mini_bsz=16

rollout_n=4
max_assistant_turns=64
max_user_turns=128
total_epochs=10
train_prompt_bsz=32 # batch size for each step
ppo_mini_batch_size=8 # 内层循环，每次roll out之后进行参数更新的mini batch size
ppo_micro_batch_size=8 # 这个影响梯度累计次数，每一次前向计算的batch size。不影响收敛性
use_dynamic_bsz=True # 如果use_dynamic_bsz开启，则ppo_micro_batch_size会失效
max_token_len=$((max_prompt_length + max_response_length))







# Algorithm parameters
temperature=1.0
top_p=1.0
top_k=-1 # 0 for HF rollout, -1 for vLLM rollout
val_top_p=0.7

use_dynamic_bsz=True
actor_ppo_max_token_len=$(((max_prompt_length + max_response_length) * 10 / 10))
infer_ppo_max_token_len=$(((max_prompt_length + max_response_length) * 1))
offload=True
OPTIM_OFFLOAD=False
optimizer_offload_fraction=0.7
last_layer=10
gen_tp=8
train_tp=4
train_pp=8
EP=4
ETP=1
CP=1

# 构建训练命令（原run_arc_7b.sh内容）
cmd="# pip install -e $verl_path --no-deps

# export VERL_PPO_LOGGING_LEVEL=DEBUG
# export HYDRA_FULL_ERROR=1
# export CUDA_DEVICE_MAX_CONNECTIONS=1
# export NCCL_NVLS_ENABLE=0
# export WANDB_API_KEY=$WANDB_API_KEY
# export VLLM_ATTENTION_BACKEND=XFORMERS

train_files=\"['$DATA_TRAIN_FILE_PATH']\"
test_files=\"['$DATA_VAL_FILE_PATH']\"

set -x

chmod -R 777 $verl_path/outputs


python -m verl.trainer.main_ppo \\
    --config-path="$CONFIG_PATH" \\
    --config-name="$CONFIG_NAME" \\
    actor_rollout_ref.rollout.multi_turn.enable=True \\
    actor_rollout_ref.rollout.multi_turn.tool_config_path=$TOOL_CONFIG_PATH \\
    actor_rollout_ref.rollout.multi_turn.tokenization_sanity_check_mode=ignore_strippable \\
    actor_rollout_ref.rollout.multi_turn.max_assistant_turns=$max_assistant_turns \\
    actor_rollout_ref.rollout.multi_turn.max_user_turns=$max_user_turns \\
    algorithm.adv_estimator=${adv_estimator} \\
    algorithm.use_kl_in_reward=${use_kl_in_reward} \\
    algorithm.kl_ctrl.kl_coef=${kl_coef} \\
    data.train_files=\"\$train_files\" \\
    data.val_files=\"\$test_files\" \\
    +data.no_chat_template=False \\
    data.train_batch_size=$train_prompt_bsz \\
    data.val_batch_size=1024 \\
    data.truncation=left \\
    data.return_raw_chat=True \\
    data.filter_overlong_prompts=$filter_overlong_prompts \\
    data.filter_overlong_prompts_workers=8 \\
    data.max_prompt_length=$max_prompt_length \\
    data.max_response_length=$max_response_length \\
    actor_rollout_ref.rollout.response_length=$max_response_length \\
    trainer.default_hdfs_dir=null \\
    trainer.default_local_dir=$verl_data_path/ckpts/$experiment_name \\
    trainer.rollout_data_dir=$verl_data_path/ckpts/$experiment_name/rollout \\
    actor_rollout_ref.model.path=$MODEL_PATH \\
    actor_rollout_ref.actor.megatron.use_dist_checkpointing=False \\
    actor_rollout_ref.actor.megatron.dist_checkpointing_path=$MODEL_PATH \\
    actor_rollout_ref.actor.optim.lr=1e-6 \\
    actor_rollout_ref.actor.optim.lr_warmup_steps=10 \\
    actor_rollout_ref.actor.optim.weight_decay=0.1 \\
    +actor_rollout_ref.actor.optim.override_optimizer_config.optimizer_offload_fraction=${optimizer_offload_fraction} \
    +actor_rollout_ref.actor.optim.override_optimizer_config.overlap_cpu_optimizer_d2h_h2d=True \
    +actor_rollout_ref.actor.optim.override_optimizer_config.use_precision_aware_optimizer=True \
    +actor_rollout_ref.actor.optim.override_optimizer_config.optimizer_cpu_offload=True \
    actor_rollout_ref.actor.use_fused_kernels=True \\
    actor_rollout_ref.actor.megatron.use_mbridge=True \\
    actor_rollout_ref.actor.use_kl_loss=${use_kl_loss} \\
    actor_rollout_ref.actor.kl_loss_coef=${kl_loss_coef} \\
    actor_rollout_ref.actor.clip_ratio_low=${clip_ratio_low} \\
    actor_rollout_ref.actor.clip_ratio_high=${clip_ratio_high} \\
    actor_rollout_ref.actor.clip_ratio_c=10.0 \\
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=2 \\
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=4 \\
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=4 \\
    actor_rollout_ref.actor.use_dynamic_bsz=${use_dynamic_bsz} \\
    actor_rollout_ref.ref.log_prob_use_dynamic_bsz=${use_dynamic_bsz} \\
    actor_rollout_ref.rollout.log_prob_use_dynamic_bsz=${use_dynamic_bsz} \\
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=${actor_ppo_max_token_len} \\
    actor_rollout_ref.ref.log_prob_max_token_len_per_gpu=${infer_ppo_max_token_len} \\
    actor_rollout_ref.rollout.log_prob_max_token_len_per_gpu=${infer_ppo_max_token_len} \\
    actor_rollout_ref.actor.ppo_mini_batch_size=${train_prompt_mini_bsz} \\
    actor_rollout_ref.actor.optim.clip_grad=1.0 \\
    actor_rollout_ref.actor.entropy_coeff=0 \\
    actor_rollout_ref.actor.loss_agg_mode=$loss_agg_mode \\
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \\
    actor_rollout_ref.actor.megatron.param_offload=${offload} \\
    actor_rollout_ref.actor.megatron.optimizer_offload=${OPTIM_OFFLOAD} \\
    actor_rollout_ref.actor.megatron.grad_offload=${offload} \\
    actor_rollout_ref.actor.megatron.pipeline_model_parallel_size=${train_pp} \\
    actor_rollout_ref.actor.megatron.tensor_model_parallel_size=${train_tp} \\
    actor_rollout_ref.actor.megatron.expert_model_parallel_size=$EP \\
    actor_rollout_ref.actor.megatron.expert_tensor_parallel_size=$ETP \\
    actor_rollout_ref.actor.megatron.context_parallel_size=${CP} \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.apply_rope_fusion=True \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.masked_softmax_fusion=True \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.bias_activation_fusion=True \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.bias_dropout_fusion=True \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.gradient_accumulation_fusion=True \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.deallocate_pipeline_outputs=True \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.persist_layer_norm=True \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.moe_grouped_gemm=True \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.moe_permute_fusion=True \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.moe_token_dispatcher_type="flex" \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.moe_router_dtype=fp32 \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.moe_enable_deepep=True \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.account_for_loss_in_pipeline_split=True \\
    +actor_rollout_ref.actor.megatron.override_transformer_config.account_for_embedding_in_pipeline_split=True \\
    actor_rollout_ref.ref.megatron.pipeline_model_parallel_size=${train_pp} \\
    actor_rollout_ref.ref.megatron.tensor_model_parallel_size=${train_tp} \\
    actor_rollout_ref.ref.megatron.expert_model_parallel_size=$EP \\
    actor_rollout_ref.ref.megatron.expert_tensor_parallel_size=$ETP \\
    actor_rollout_ref.ref.megatron.context_parallel_size=${CP} \\
    actor_rollout_ref.ref.megatron.param_offload=${offload} \\
    reward_model.reward_manager=dapo \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.enable=${enable_overlong_buffer} \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.len=${overlong_buffer_len} \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.penalty_factor=${overlong_penalty_factor} \\
    +reward_model.reward_kwargs.overlong_buffer_cfg.log=False \\
    +reward_model.reward_kwargs.max_resp_len=${max_response_length} \\
    actor_rollout_ref.rollout.tensor_model_parallel_size=${gen_tp} \\
    actor_rollout_ref.rollout.disable_log_stats=True \\
    actor_rollout_ref.rollout.name=vllm  \\
    actor_rollout_ref.rollout.max_num_batched_tokens=$max_token_len \\
    actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \\
    actor_rollout_ref.rollout.n=$rollout_n \\
    actor_rollout_ref.rollout.temperature=${temperature} \\
    actor_rollout_ref.rollout.top_p=${top_p} \\
    actor_rollout_ref.rollout.top_k=${top_k} \\
    actor_rollout_ref.nccl_timeout=1200 \\
    actor_rollout_ref.rollout.val_kwargs.temperature=${temperature} \\
    actor_rollout_ref.rollout.val_kwargs.top_p=${val_top_p} \\
    actor_rollout_ref.rollout.val_kwargs.top_k=${top_k} \\
    actor_rollout_ref.rollout.val_kwargs.do_sample=True \\
    actor_rollout_ref.rollout.val_kwargs.n=1 \\
    actor_rollout_ref.rollout.enable_chunked_prefill=True \\
    actor_rollout_ref.rollout.enforce_eager=True \\
    actor_rollout_ref.rollout.free_cache_engine=True \\
    algorithm.kl_ctrl.kl_coef=$kl_coef \\
    trainer.critic_warmup=0 \\
    trainer.logger=['console'] \\
    trainer.project_name=$project_name \\
    trainer.experiment_name=$experiment_name \\
    trainer.val_before_train=False \\
    trainer.n_gpus_per_node=$worker_gpu \\
    trainer.nnodes=$worker_count \\
    trainer.save_freq=50 \\
    trainer.test_freq=10 \\
    trainer.total_epochs=$total_epochs \\
    trainer.resume_mode=auto \\
    trainer.log_val_generations=10 \$@"


echo "$cmd" > ./training_configs/$experiment_name.sh

bash_command="cd $verl_path && python examples/start_train_yidian.py 'sh ./training_configs/$experiment_name.sh' $worker_count"



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


