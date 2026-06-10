verl_path=${PROJECT_DIR}
hf_model_path=${PROJECT_DIR}
output_path=${PROJECT_DIR}
job_name=convert-hf-to-mcore-$(date +%m%d-%H%M)
mkdir -p $output_path



bash_command="export PIP_TIMEOUT=600 && 
export PIP_INDEX_URL=https://pypi.org/simple && 
export PIP_EXTRA_INDEX_URL=https://pypi.org/simple && 
export PIP_TRUSTED_HOST='pypi.org' && cd '$verl_path'
pip install -e '$verl_path' --no-deps && 
python $verl_path/scripts/converter_hf_to_mcore.py \
    --hf_model_path $hf_model_path \
    --output_path $output_path \
    --use_cpu_initialization

cp -r $hf_model_path/!(*.safetensors) $output_path/
"

set -ex
worker_count=1 # Task Replicas
worker_gpu=1
worker_cpu=32
worker_memory_GB=256
namespace=ailab-llmbr # ailab-puyullmgpu ailab-llmbr
quota_group=llmbr_gpu # puyullm_gpu llmbr_gpu
image=<CONTAINER_IMAGE>
# <CONTAINER_IMAGE>
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

rjob submit -e DISTRIBUTED_JOB=true \
    --image-pull-policy=Always \
    --namespace=$namespace \
    --image=$image \
    --host-network=false --name $job_name -P $worker_count --gpu $worker_gpu --cpu $worker_cpu --memory $((worker_memory_GB * 1024)) --charged-group $quota_group \
    --private-machine='group' \
    --mount=gpfs://gpfs1/<USER>:${USER_STORAGE} \
    --mount=gpfs://<GPFS_WORKSPACE>:${SHARED_WORKSPACE} \
    --custom-resources rdma/mlnx_shared=8 \
    --custom-resources mellanox.com/mlnx_rdma=1 \
    --enable-lxcfs=false \
    --auto-restart=$auto_restart \
    --preemptible=$preemptible \
    --restart-policy=$restart_policy \
    --backoff_limit=$backoff_limit \
    --enable-self-health=$enable_self_health \
    --self-health-count=$self_health_count \
    --grace-period-minutes=$grace_period_minutes \
    --termination-grace-period-minutes=$termination_grace_period_minutes \
    --priority=9 \
    -- bash -ecx "$bash_command"