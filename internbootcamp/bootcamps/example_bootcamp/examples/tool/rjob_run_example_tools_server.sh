#!/bin/bash

job_name="example_bootcamp-tool-master-$(date +%Y%m%d%H%M%S)"

prj_path=${PROJECT_DIR}
tools_yaml_path=${prj_path}/internbootcamp/bootcamps/example_bootcamp/configs/example_tool_config.yaml
tool_master_port=20148
timeout_per_query=90
zombie_instance_timeout=600
heartbeat_timeout=6
health_check_interval=1
recovery_wait_timeout=60
recovery_wait_interval=1.0

set -ex
worker_cpu=4
worker_memory_GB=8
namespace=ailab-llmbr
quota_group=llmbr_gpu
image=<CONTAINER_IMAGE>
preemptible=no # yes no

# 容器级别重启
auto_restart=false # false true always;  always表示无论什么原因导致任务退出都重启
restart_policy=never # 重启策略：(choose from 'never', 'onfailure', 'restartjobonfailure')
backoff_limit=9999 # 任务失败重试次数

# 仪电推荐的job级别的重启("自愈")
enable_self_health=false
self_health_count=9999
grace_period_minutes=10
termination_grace_period_minutes=3

bash_command="cd $prj_path && export PIP_INDEX_URL=https://pypi.org/simple && export PIP_EXTRA_INDEX_URL=https://pypi.org/simple && export PIP_TRUSTED_HOST='pypi.org' && pip install -e $prj_path/verl --no-deps && export PYTHONUNBUFFERED=1 && python -u -m internbootcamp.utils.tool_server.cli --log_dir internbootcamp/bootcamps/example_bootcamp/data/tool_server_logs --tools_yaml_path $tools_yaml_path --port $tool_master_port --mode master --timeout_per_query $timeout_per_query --zombie_instance_timeout $zombie_instance_timeout --heartbeat_timeout $heartbeat_timeout --health_check_interval $health_check_interval --recovery_wait_timeout $recovery_wait_timeout --recovery_wait_interval $recovery_wait_interval"

# eval "$bash_command"

rjob submit -e DISTRIBUTED_JOB=true \
    --namespace=$namespace \
    --image=$image \
    --host-network=true --name $job_name --gpu 0 --cpu $worker_cpu --memory $((worker_memory_GB * 1024)) --charged-group $quota_group \
    --private-machine='group' \
    --gang-start=false \
    --enable-sshd \
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
