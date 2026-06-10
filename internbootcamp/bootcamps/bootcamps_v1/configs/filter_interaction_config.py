import yaml
import json
import os
import re

def extract_algo_name_from_class(class_name):
    # 匹配: internbootcamp.bootcamps.bootcamps_v1.<any_module>.<algo_name>
    # 只提取最后一部分（即 <algo_name>）
    match = re.search(r'^verl\.internbootcamp\.bootcamps\.bootcamps_v1\.[^.]+\.([^.]+)', class_name)
    if match:
        return match.group(1).lower()
    return None

def extract_algo_name_from_jsonl_path(yaml_interaction_path):
    # 路径示例: internbootcamp/bootcamps/bootcamps_v1/algorithm/fchaoticv/configs/...
    # 或:       internbootcamp/bootcamps/bootcamps_v1/model/random_forest/...
    parts = yaml_interaction_path.split('/')
    try:
        # 找到 'bootcamps_v1' 的位置
        idx = parts.index('bootcamps_v1')
        # 确保后面至少还有两级: <module>/<algo_name>/...
        if idx + 2 < len(parts):
            algo_name = parts[idx + 2]  # idx+1 是 module，idx+2 是 algo_name
            return algo_name.lower()
    except ValueError:
        pass
    return None

# 读取 JSONL 文件，构建允许的算法名集合
allowed_algo_names = set()
jsonl_path = '${PROJECT_DIR}'
with open(jsonl_path, 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip():
            continue
        data = json.loads(line)
        algo = extract_algo_name_from_jsonl_path(data.get('yaml_interaction_path', ''))
        if algo:
            allowed_algo_names.add(algo)

# 读取原始 YAML
yaml_input_path = '${PROJECT_DIR}'
with open(yaml_input_path, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# 筛选 interaction
filtered_interactions = []
for item in data.get('interaction', []):
    class_name = item.get('class_name', '')
    algo = extract_algo_name_from_class(class_name)
    if algo and algo in allowed_algo_names:
        filtered_interactions.append(item)

# 写回 YAML
output = {'interaction': filtered_interactions}
yaml_output_path = '${PROJECT_DIR}'
with open(yaml_output_path, 'w', encoding='utf-8') as f:
    yaml.dump(output, f, default_flow_style=False, sort_keys=False, allow_unicode=True)