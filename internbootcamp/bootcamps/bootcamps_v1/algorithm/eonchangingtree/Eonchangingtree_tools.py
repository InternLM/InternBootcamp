import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.eonchangingtree.Eonchangingtree_reward_calculator import EonchangingtreeRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

mod = 10**9 + 7



# === 源文件中的全局函数 ===

def build_adj(parents, n):
    adj = {i: [] for i in range(1, n+1)}
    for i in range(2, n+1):
        parent = parents[i-2]
        adj[parent].append(i)
    return adj

def dfs(x, parent_adj, tin, tout, dep, current_time, current_g):
    current_time[0] += 1
    tin[x] = current_time[0]
    dep[tin[x]] = current_g
    for child in parent_adj.get(x, []):
        dfs(child, parent_adj, tin, tout, dep, current_time, current_g-1)
    tout[x] = current_time[0]

def perform_dfs(n, parent_adj):
    tin = [0] * (n + 1)
    tout = [0] * (n + 1)
    dep = [0] * (n + 2)  # tin values are 1-based
    current_time = [0]
    dfs(1, parent_adj, tin, tout, dep, current_time, n)
    return tin, tout, dep

def process_queries_for_identity(queries, n, tin_dict, tout_dict, dep_list):
    a = [0] * (n + 2)
    b = [0] * (n + 2)
    expected_outputs = []
    for query in queries:
        if query['type'] == 1:
            v = query['v']
            x = query['x']
            k = query['k']
            tin_v = tin_dict[v]
            tout_v = tout_dict[v]
            f1 = (x - dep_list[tin_v] * k) % mod
            f2 = k % mod
            for u in range(1, n+1):
                u_tin = tin_dict[u]
                if tin_v <= u_tin <= tout_v:
                    a[u_tin] = (a[u_tin] + f1) % mod
                    b[u_tin] = (b[u_tin] + f2) % mod
        else:
            v = query['v']
            u_tin = tin_dict[v]
            res = (a[u_tin] + b[u_tin] * dep_list[u_tin]) % mod
            expected_outputs.append(res)
    return expected_outputs

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EonchangingtreeVerificationTool(BaseTool):
    """Eonchangingtree验证工具"""
    
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
            score = EonchangingtreeRewardCalculator.verify_score(
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
            logger.error(f"EonchangingtreeVerificationTool执行错误: {str(e)}")
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

