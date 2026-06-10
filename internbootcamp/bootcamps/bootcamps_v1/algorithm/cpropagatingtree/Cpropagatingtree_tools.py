import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cpropagatingtree.Cpropagatingtree_reward_calculator import CpropagatingtreeRewardCalculator

# 导入依赖库
import random

# === 源文件中的其他类 ===

class FenwickTree:
    def __init__(self, size):
        self.n = size
        self.tree = [0] * (self.n + 2)  # 1-based indexing

    def update_point(self, idx, delta):
        while idx <= self.n:
            self.tree[idx] += delta
            idx += idx & -idx

    def query_prefix(self, idx):
        res = 0
        while idx > 0:
            res += self.tree[idx]
            idx -= idx & -idx
        return res

    def update_range(self, l, r, delta):
        self.update_point(l, delta)
        self.update_point(r + 1, -delta)

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CpropagatingtreeVerificationTool(BaseTool):
    """Cpropagatingtree验证工具"""
    
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
            score = CpropagatingtreeRewardCalculator.verify_score(
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
            logger.error(f"CpropagatingtreeVerificationTool执行错误: {str(e)}")
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
    def generate_tree(self, n):
        if n == 1:
            return []
        edges = []
        nodes = [1]
        for i in range(2, n + 1):
            parent = random.choice(nodes)
            edges.append((parent, i))
            nodes.append(i)
        return edges

    def simulate_case(self, case):
        n, a = case['n'], case['a']
        edges, queries = case['edges'], case['queries']
        tree = [[] for _ in range(n + 1)]
        for u, v in edges:
            tree[u].append(v)
            tree[v].append(u)

        # Euler Tour初始化
        euler = [-1]
        idx = [0] * (n + 1)
        child = [0] * (n + 1)
        parity = [0] * (n + 1)
        vst = [False] * (n + 1)

        def dfs(u, depth):
            vst[u] = True
            parity[u] = depth % 2
            idx[u] = len(euler)
            euler.append(u)
            child[u] = 1
            for v in tree[u]:
                if not vst[v] and v != u:
                    dfs(v, depth + 1)
                    child[u] += child[v]

        dfs(1, 0)
        max_size = len(euler) - 1

        # 初始化两个BIT
        bit0 = FenwickTree(max_size)
        bit1 = FenwickTree(max_size)
        expected = []

        # 处理查询
        for query in queries:
            if query[0] == '1':
                x = int(query[1])
                val = int(query[2])
                p = parity[x]
                L = idx[x]
                R = L + child[x] - 1  # 闭区间

                if p == 0:
                    bit0.update_range(L, R, val)
                    bit1.update_range(L, R, -val)
                else:
                    bit1.update_range(L, R, val)
                    bit0.update_range(L, R, -val)
            else:
                x = int(query[1])
                p = parity[x]
                sum_p = bit0.query_prefix(idx[x]) if p == 0 else bit1.query_prefix(idx[x])
                expected.append(a[x-1] + sum_p)
        return expected
