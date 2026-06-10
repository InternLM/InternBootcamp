import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.binvarianceoftree.Binvarianceoftree_reward_calculator import BinvarianceoftreeRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import re

# === 源文件中的全局函数 ===

def check_permutation_solution(n, p_list_1based):
    if n == 0:
        return (False, [])
    p_list = [x - 1 for x in p_list_1based]  # Convert to 0-based
    was = [False] * n
    cyc = defaultdict(list)

    # Find all cycles
    for i in range(n):
        if was[i]:
            continue
        cycle = []
        j = i
        while not was[j]:
            was[j] = True
            cycle.append(j)
            j = p_list[j]
        cyc[len(cycle)].append(cycle)
    
    lengths = sorted(cyc.keys(), reverse=True)
    parent = {}
    roots = []
    
    # Determine parents for each cycle length
    for l in lengths:
        found = False
        for m in lengths:
            if m < l and l % m == 0:
                parent[l] = m
                found = True
                break
        if not found:
            parent[l] = None
            roots.append(l)
    
    # Check validity of roots
    if len(roots) > 1 or (len(roots) == 1 and roots[0] > 2):
        return (False, None)
    
    # Construct the tree edges
    edges = []
    if roots:
        root_len = roots[0]
    else:
        return (False, None)
    
    # Handle root cycle(s)
    if root_len == 2:
        root_cycle = cyc[2][0]
        edges.append((root_cycle[0], root_cycle[1]))
        for cycle in cyc[2][1:]:
            edges.append((root_cycle[0], cycle[0]))
            edges.append((root_cycle[1], cycle[1]))
    elif root_len == 1 and 1 in cyc:
        main_node = cyc[1][0][0]
        for cycle in cyc[1][1:]:
            edges.append((main_node, cycle[0]))
    
    # Attach other cycles to their parents
    for l in lengths:
        if l == root_len:
            continue
        if l not in parent:
            continue
        parent_len = parent[l]
        if parent_len is None:
            continue
        parent_cycles = cyc[parent_len]
        for cycle in cyc[l]:
            for i in range(len(cycle)):
                parent_node = parent_cycles[0][i % parent_len]
                edges.append((parent_node, cycle[i]))
    
    # Convert edges back to 1-based
    edges_1based = [(u + 1, v + 1) for u, v in edges]
    return (True, edges_1based)

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class BinvarianceoftreeVerificationTool(BaseTool):
    """Binvarianceoftree验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = BinvarianceoftreeRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"BinvarianceoftreeVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
    # 其他额外方法

