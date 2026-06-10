import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cilyaandthetree.Cilyaandthetree_reward_calculator import CilyaandthetreeRewardCalculator

# 导入依赖库
import random
import math
import re
from typing import List
from typing import Dict
from typing import Any
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CilyaandthetreeVerificationTool(BaseTool):
    """Cilyaandthetree验证工具"""
    
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
            score = CilyaandthetreeRewardCalculator.verify_score(
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
            logger.error(f"CilyaandthetreeVerificationTool执行错误: {str(e)}")
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
    def _generate_valid_tree(self, n: int) -> List[List[int]]:
        """生成以1为根的合法树结构"""
        if n == 1:
            return []

        nodes = list(range(2, n+1))
        random.shuffle(nodes)
        edges = []
        connected = {1}
        for node in nodes:
            parent = random.choice(list(connected))
            edges.append([parent, node])
            connected.add(node)
        return edges

    def _compute_solution(self, n: int, a: List[int], edges: List[List[int]]) -> List[int]:
        """正确实现参考算法逻辑"""
        # 构建邻接表（1-based）
        adj = defaultdict(list)
        for x, y in edges:
            adj[x].append(y)
            adj[y].append(x)

        # 初始化数据结构
        res = [0] * (n+1)  # 1-based索引
        res[1] = a[0]
        cnt = defaultdict(int)
        max_depth = defaultdict(int)

        # 预计算根节点所有因数
        root_val = a[0]
        divisors = set()
        d = 1
        while d*d <= root_val:
            if root_val % d == 0:
                divisors.add(d)
                if d != root_val//d:
                    divisors.add(root_val//d)
            d += 1

        # 初始化因数计数
        for d in divisors:
            cnt[d] = 1

        # DFS遍历
        stack = [(1, 0, root_val)]  # (current, parent, current_gcd)
        path = []

        while stack:
            node, parent, current_gcd = stack.pop()
            path.append(node)

            # 计算当前路径长度
            current_depth = len(path)

            # 计算当前节点的可能最大值
            max_val = current_gcd
            for d in sorted(divisors, reverse=True):
                if cnt[d] >= current_depth - 1:
                    max_val = max(max_val, d)
                    break

            res[node] = max_val

            # 处理子节点
            for child in adj[node]:
                if child == parent:
                    continue

                # 计算子节点的GCD
                child_gcd = math.gcd(current_gcd, a[child-1])

                # 更新因数计数
                for d in divisors:
                    if a[child-1] % d == 0:
                        cnt[d] += 1

                stack.append((child, node, child_gcd))

            # 回溯时恢复计数
            if path:
                last_node = path.pop()
                for d in divisors:
                    if a[last_node-1] % d == 0:
                        cnt[d] = max(cnt[d]-1, 0)

        return [res[i] for i in range(1, n+1)]
