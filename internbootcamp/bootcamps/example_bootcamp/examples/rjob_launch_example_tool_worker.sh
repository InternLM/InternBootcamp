#!/bin/bash


job_name="bootcamp-tool-worker-$(date +%Y%m%d%H%M%S)"

prj_path=${PROJECT_DIR}
tools_yaml_path=internbootcamp/bootcamps/example_bootcamp/configs/example_tool_config.yaml
num_tool_workers=1
tool_worker_start_port=19600
tool_master_url=http://10.102.251.33:20148

set -ex
worker_count=4 # Task Replicas
worker_gpu=0
worker_cpu=1
worker_memory_GB=4
namespace=ailab-llmbr #ailab-puyullmgpunew
quota_group=llmbr_gpu # puyullm_gpu llmbr_gpu
image=<CONTAINER_IMAGE>
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


bash_command="cd $prj_path && export PIP_INDEX_URL=https://pypi.org/simple && export PIP_EXTRA_INDEX_URL=https://pypi.org/simple && export PIP_TRUSTED_HOST='pypi.org' && pip install -e $prj_path/verl --no-deps && export PYTHONUNBUFFERED=1 && python -u -m internbootcamp.utils.tool_server.cli  --tools_yaml_path $tools_yaml_path --port  $tool_worker_start_port  --mode worker   --master_url $tool_master_url   --num_workers $num_tool_workers"




rjob submit -e DISTRIBUTED_JOB=true \
    --namespace=$namespace \
    --image=$image \
    --host-network=false --name $job_name -P $worker_count --gpu $worker_gpu --cpu $worker_cpu --memory $((worker_memory_GB * 1024)) --charged-group $quota_group \
    --private-machine='group' \
    --gang-start=false \
    --mount=gpfs://gpfs1/<USER>:${USER_STORAGE} \
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





# Rjob 在提交的时候，加上-ｅ DISTRIBUTED_JOB=true平台会自动注入环境变量，在任务容器里，会设置以下环境变量来方便用户拼凑多机任务启动命令行：
#     # 多机任务配置信息
#     NODE_RANK=xx # 当前节点Rank, 0,1,2,3,4 ${NODE_RANK}
#     NODE_COUNT=xx # 总节点数, 8,16
#     MASTER_ADDR=xxx # Rank0所在节点地址
#     PROC_PER_NODE=xx # 每机rank数（卡数）
#     JOB_ID=xxxxxx # 当前任务ID，可供任务做按job识别之用
    
#     # RDMA通信环境变量。集群各种机型配置都不尽相同，请勿覆盖，引起不必要的通信错误
#     NCCL_SOCKET_IFNAME # NCCL建联网卡
#     NCCL_IB_HCA # RDMA设备列表
#     NCCL_IB_GID_INDEX # RDMA设备GID索引
#     CUDA_VISIBLE_DEVICES # 容器内可用CUDA设备编号