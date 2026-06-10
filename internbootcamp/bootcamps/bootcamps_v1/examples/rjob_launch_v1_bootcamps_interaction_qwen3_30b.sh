#!/bin/bash



# 任务提交参数设置（原dlc_lanuch.sh内容）
project_name=v1_bootcamps_interaction
experiment_name='v1_bootcamps_interaction-grpo-Qwen3-30B-A3B-Instruct-2507-0924'
verl_path="${PROJECT_DIR}"
cd $verl_path
worker_gpu=8
worker_count=4
worker_cpu=32
image="<CONTAINER_IMAGE>"
# WANDB_MODE=offline
WANDB_API_KEY="350272d1b727788703b1f5d46518d3c1f41b274f"
worker_memory_GB=256
namespace=ailab-llmbr
quota_group=llmbr_gpu # puyullm_gpu llmbr_gpu
# mount=gpfs://gpfs1/<USER>:${USER_STORAGE},gpfs://<GPFS_WORKSPACE>:${SHARED_WORKSPACE},gpfs://gpfs1/large-model-center-share-weights:${MODEL_STORAGE}
preemptible=no # yes no
# 容器级别重启
auto_restart=false # false true always;  always表示无论什么原因导致任务退出都重启
restart_policy=never # 重启策略：(choose from 'never', 'onfailure', 'restartjobonfailure')
# Always : 只要 Pod 中的容器终止运行（无论退出代码是什么，0 还是非 0），kubelet（节点上的代理）都会自动重启该容器。
# OnFailure: 只有当 Pod 中的容器以非零退出代码（即失败状态）终止时，kubelet 才会重启该容器。如果容器正常退出（退出代码为 0），则不会重启
backoff_limit=9999 # 任务失败重试次数

# 仪电推荐的job级别的重启("自愈")
# https://iqeubg8au73.feishu.cn/docx/VEyddBrH5oEGlexzOVUcnlTan6x
enable_self_health=false
self_health_count=9999
grace_period_minutes=10 # 自愈介入时间，即获取到告警后，多久开始自愈
termination_grace_period_minutes=3 # 数据回收时间，发送信号-15 到容器，等待回收时间到期后开始重建任务 / 旧任务终止与新任务重启之间的等待时间,用于数据的保存或回收,超时将开始终止旧任务,并基于框架设定的策略拉起新任务



actor_model=${MODEL_PATH}
# actor_model=${PROJECT_DIR}
# actor_model=${PROJECT_DIR}
# 7B qwen必须tp4
CONFIG_PATH="${verl_path}/internbootcamp/bootcamps/bootcamps_v1/configs"
# 配置文件名
CONFIG_NAME="v1_bootcamps_multiturn_w_interaction_grpo.yaml"  
# 工具配置文件路径
## 远程工具配置文件路径
INTERACTION_CONFIG_PATH="${verl_path}/internbootcamp/bootcamps/bootcamps_v1/configs/merged_interactions.yaml"  
DATA_TRAIN_FILE_PATH="${PROJECT_DIR}"  # 训练集数据路径
# 验证集数据路径
DATA_VAL_FILE_PATH="${PROJECT_DIR}"  
filter_overlong_prompts=True




rollout_n=4
sp_size=8
gen_tp=8
total_epochs=3
clip_ratio_low=0.2
clip_ratio_high=0.28 # 不确定这个是否要提高
train_prompt_bsz=32 # batch size for each step
ppo_mini_batch_size=32 # 内层循环，每次roll out之后进行参数更新的mini batch size
ppo_micro_batch_size=32 # 这个影响梯度累计次数，每一次前向计算的batch size。不影响收敛性
use_dynamic_bsz=True # 如果use_dynamic_bsz开启，则ppo_micro_batch_size会失效
loss_agg_mode="seq-mean-token-mean" # token-mean 会熵快速升高，这个是对的
enable_overlong_buffer=False
max_prompt_length=4096
max_response_length=8192
max_token_len=$((max_prompt_length + max_response_length))
kl_coef=0.0
kl_loss_coef=0.0








# 构建训练命令（原run_arc_7b.sh内容）
cmd="# pip install -e $verl_path --no-deps

export VERL_PPO_LOGGING_LEVEL=DEBUG
export HYDRA_FULL_ERROR=1
export WANDB_API_KEY=$WANDB_API_KEY
# export VLLM_ATTENTION_BACKEND=XFORMERS

train_files=\"['$DATA_TRAIN_FILE_PATH']\"
test_files=\"['$DATA_VAL_FILE_PATH']\"

set -x

sudo chmod -R 777 $verl_path/outputs


python -m verl.trainer.main_ppo \\
    --config-path="$CONFIG_PATH" \\
    --config-name="$CONFIG_NAME" \\
    actor_rollout_ref.rollout.multi_turn.interaction_config_path=${PROJECT_DIR} \\
    algorithm.adv_estimator=grpo \\
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
    trainer.default_local_dir=$verl_path/ckpts/$experiment_name \\
    trainer.rollout_data_dir=$verl_path/ckpts/$experiment_name/rollout  \\
    actor_rollout_ref.model.path=$actor_model \\
    actor_rollout_ref.actor.optim.lr=1e-6 \\
    actor_rollout_ref.model.use_remove_padding=True \\
    actor_rollout_ref.rollout.multi_turn.tokenization_sanity_check_mode=ignore_strippable \\
    actor_rollout_ref.actor.ppo_mini_batch_size=$ppo_mini_batch_size \\
    actor_rollout_ref.actor.ppo_micro_batch_size=$ppo_micro_batch_size \\
    actor_rollout_ref.actor.use_dynamic_bsz=$use_dynamic_bsz \\
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=$max_token_len \\
    actor_rollout_ref.ref.log_prob_max_token_len_per_gpu=$max_token_len  \\
    actor_rollout_ref.ref.log_prob_use_dynamic_bsz=$use_dynamic_bsz \\
    actor_rollout_ref.rollout.log_prob_max_token_len_per_gpu=$max_token_len  \\
    actor_rollout_ref.actor.use_kl_loss=False \\
    actor_rollout_ref.actor.grad_clip=1.0 \\
    actor_rollout_ref.actor.loss_agg_mode=$loss_agg_mode \\
    actor_rollout_ref.actor.kl_loss_coef=$kl_loss_coef \\
    actor_rollout_ref.actor.clip_ratio_low=$clip_ratio_low \\
    actor_rollout_ref.actor.clip_ratio_high=$clip_ratio_high \\
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \\
    actor_rollout_ref.model.enable_gradient_checkpointing=True \\
    actor_rollout_ref.actor.fsdp_config.param_offload=True \\
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \\
    actor_rollout_ref.actor.entropy_checkpointing=True \\
    actor_rollout_ref.actor.entropy_from_logits_with_chunking=True \\
    actor_rollout_ref.rollout.tensor_model_parallel_size=$gen_tp \\
    actor_rollout_ref.actor.ulysses_sequence_parallel_size=${sp_size} \\
    actor_rollout_ref.rollout.disable_log_stats=True \\
    actor_rollout_ref.rollout.name=sglang  \\
    actor_rollout_ref.rollout.max_num_batched_tokens=$max_token_len \\
    actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \\
    actor_rollout_ref.rollout.n=$rollout_n \\
    actor_rollout_ref.rollout.temperature=1 \\
    actor_rollout_ref.rollout.top_p=0.9 \\
    actor_rollout_ref.rollout.top_k=-1 \\
    actor_rollout_ref.rollout.enable_chunked_prefill=True \\
    actor_rollout_ref.ref.fsdp_config.param_offload=True \\
    algorithm.use_kl_in_reward=False \\
    actor_rollout_ref.rollout.enforce_eager=False \\
    actor_rollout_ref.rollout.free_cache_engine=False \\
    algorithm.kl_ctrl.kl_coef=$kl_coef \\
    trainer.critic_warmup=0 \\
    trainer.logger=['console'] \\
    trainer.project_name=$project_name \\
    trainer.experiment_name=$experiment_name \\
    trainer.val_before_train=False \\
    trainer.n_gpus_per_node=$worker_gpu \\
    trainer.nnodes=$worker_count \\
    trainer.save_freq=10 \\
    trainer.test_freq=9999999 \\
    trainer.total_epochs=$total_epochs \$@"


echo "$cmd" > ./training_configs/$experiment_name.sh

bash_command="cd $verl_path && python examples/start_train_yidian.py 'sh ./training_configs/$experiment_name.sh' $worker_count"



rjob submit -e DISTRIBUTED_JOB=true \
    --namespace=$namespace  \
    --image=$image \
    --host-network=true --name $experiment_name -P $worker_count --gpu $worker_gpu --cpu $worker_cpu --memory $((worker_memory_GB * 1024)) --charged-group $quota_group \
    --private-machine='group' \
    --gang-start=true \
    --mount=gpfs://gpfs1/<USER>:${USER_STORAGE} \
    --mount=gpfs://<GPFS_WORKSPACE>:${SHARED_WORKSPACE} \
    --mount=gpfs://gpfs1/large-model-center-share-weights:${MODEL_STORAGE} \
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


