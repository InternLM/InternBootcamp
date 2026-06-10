#!/usr/bin/env bash

set -euo pipefail

# ---------------------------------------------------------------------------
# 极简 rjob 提交脚本模板
#
# - 如需修改资源或镜像，直接调整下方常量或在调用前通过环境变量覆盖。
# - 默认会将指定目录打包上传，请确认没有不需要的文件。
# - 任务执行逻辑会写入 JOB_FOLDER 下的临时脚本，由 rjob 在远端执行。
# ---------------------------------------------------------------------------

# ------------------------ 常用参数（可覆盖） --------------------------------
JOB_NAME=${JOB_NAME:-"${USER:-user}-$(date +%Y%m%d-%H%M%S)"}
JOB_GROUP=${JOB_GROUP:-"llmbr-gpu"}              # 为空则不传该参数
JOB_NAMESPACE=${JOB_NAMESPACE:-"ailab-llmbr"}
JOB_DELETE_EXISTING=${JOB_DELETE_EXISTING:-"false"}

TASK_IMAGE=${TASK_IMAGE:-"<CONTAINER_IMAGE>"}
TASK_CPU=${TASK_CPU:-16}
TASK_GPU=${TASK_GPU:-1}
TASK_MEMORY=${TASK_MEMORY:-820}      # 单位: GB
TASK_MEMORY=$((TASK_MEMORY * 1024)) # 转换为 MiB
TASK_CHARGED_GROUP=${TASK_CHARGED_GROUP:-"llmbr_gpu"}
TASK_PRIVATE_MACHINE=${TASK_PRIVATE_MACHINE:-"group"}
TASK_MOUNTS=${TASK_MOUNTS:-"gpfs://<GPFS_WORKSPACE>:${SHARED_WORKSPACE} gpfs://gpfs1/<USER>:${USER_STORAGE} gpfs://gpfs1/large-model-center-share-weights:${MODEL_STORAGE}"}
TASK_ENVS=${TASK_ENVS:-""}              # 环境变量，例如：TASK_ENVS="ENV1=V1 ENV2=V2"

# ---------------------------------------------------------------------------
# 将任务命令写入 JOB_FOLDER 内的临时脚本，供 rjob 在远端执行
# 可通过 TASK_SCRIPT_NAME 覆盖脚本文件名，通过 TASK_CMD_BODY 覆盖脚本内容
# ---------------------------------------------------------------------------
JOB_FOLDER="${PROJECT_DIR}"
timestamp=$(date +%Y%m%d%H%M%S)
TASK_SCRIPT_NAME=${TASK_SCRIPT_NAME:-"rjob_task_cmd_${timestamp}.sh"}
TASK_SCRIPT_PATH="${JOB_FOLDER}/${TASK_SCRIPT_NAME}"

mkdir -p "${JOB_FOLDER}"

if [[ -z "${TASK_CMD_BODY:-}" ]]; then
  read -r -d '' TASK_CMD_BODY <<'EOF' || true
#!/usr/bin/env bash
set -euo pipefail

cd ${PROJECT_DIR}

python -m verl.model_merger merge \
  --backend megatron \
  --local_dir verl-cache/ckpts/acs-grpo-Qwen3-235B-mix-single-round-hard-1115/global_step_120/actor \
  --target_dir verl-cache/ckpts/acs-grpo-Qwen3-235B-mix-single-round-hard-1115/global_step_120/actor_hf_model \
  --use_cpu_initialization
EOF
fi

printf '%s\n' "${TASK_CMD_BODY}" > "${TASK_SCRIPT_PATH}"
chmod +x "${TASK_SCRIPT_PATH}"

TASK_CMD=("bash" "${TASK_SCRIPT_PATH}")

# ---------------------------- 拼接参数 --------------------------------------
declare -a RJOB_FLAGS

RJOB_FLAGS+=(--name "${JOB_NAME}")
[[ -n "${JOB_GROUP}" ]] && RJOB_FLAGS+=(--group "${JOB_GROUP}")
[[ -n "${JOB_NAMESPACE}" ]] && RJOB_FLAGS+=(--namespace "${JOB_NAMESPACE}")
[[ "${JOB_DELETE_EXISTING}" == "true" ]] && RJOB_FLAGS+=(--delete)

RJOB_FLAGS+=(--task_name main)
RJOB_FLAGS+=(--image "${TASK_IMAGE}")
RJOB_FLAGS+=(--folder "${JOB_FOLDER}")
RJOB_FLAGS+=(--cpu "${TASK_CPU}")
RJOB_FLAGS+=(--gpu "${TASK_GPU}")
RJOB_FLAGS+=(--memory "${TASK_MEMORY}")
RJOB_FLAGS+=(--restart-policy never)
RJOB_FLAGS+=(--replicas 1)
[[ -n "${TASK_CHARGED_GROUP}" ]] && RJOB_FLAGS+=(--charged-group "${TASK_CHARGED_GROUP}")
[[ -n "${TASK_PRIVATE_MACHINE}" ]] && RJOB_FLAGS+=(--private-machine "${TASK_PRIVATE_MACHINE}")

if [[ -n "${TASK_MOUNTS}" ]]; then
  for mount in ${TASK_MOUNTS}; do
    RJOB_FLAGS+=(--mount "${mount}")
  done
fi

if [[ -n "${TASK_ENVS}" ]]; then
  for env_kv in ${TASK_ENVS}; do
    RJOB_FLAGS+=(--set-env "${env_kv}")
  done
fi

# ------------------------------ 提交 ----------------------------------------
echo "+ rjob submit ${RJOB_FLAGS[*]} -- ${TASK_CMD[*]}"
rjob submit "${RJOB_FLAGS[@]}" -- "${TASK_CMD[@]}"

