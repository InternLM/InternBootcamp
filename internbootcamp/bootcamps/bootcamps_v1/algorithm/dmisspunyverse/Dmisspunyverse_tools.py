import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dmisspunyverse.Dmisspunyverse_reward_calculator import DmisspunyverseRewardCalculator

# 导入依赖库
import random
from sys import setrecursionlimit



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DmisspunyverseVerificationTool(BaseTool):
    """Dmisspunyverse验证工具"""
    
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
            score = DmisspunyverseRewardCalculator.verify_score(
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
            logger.error(f"DmisspunyverseVerificationTool执行错误: {str(e)}")
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
    def generate_tree_edges(self, n):
        """生成合法的树结构，节点编号从1开始"""
        if n == 1:
            return []
        edges = []
        parents = list(range(n))
        for i in range(1, n):
            parents[i] = random.randint(0, i-1)
        # 转换为1-based节点编号
        for i in range(1, n):
            u = parents[i] + 1
            v = i + 1
            edges.append((u, v))
        random.shuffle(edges)
        return edges

    @staticmethod
    def solve_case(n, m, b, w, edges):
        """树形DP实现，修复状态初始化问题"""
        # 构建邻接表 (0-based)
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u-1].append(v-1)
            adj[v-1].append(u-1)

        a = [w[i] - b[i] for i in range(n)]

        # DP状态数组 (max_m+2防止越界)
        max_m = m
        dp = [[(-1, -float('inf'))] * (max_m + 2) for _ in range(n)]
        sz = [0] * n

        def dfs(parent, u):
            sz[u] = 1
            dp[u][1] = (0, a[u])  # 初始状态

            for v in adj[u]:
                if v == parent:
                    continue
                dfs(u, v)

                # 合并子树状态
                current_max = min(sz[u], max_m)
                child_max = min(sz[v], max_m)
                ndp = [(-1, -float('inf'))] * (current_max + child_max + 1)

                for i in range(1, current_max + 1):
                    if dp[u][i][0] == -1:
                        continue
                    for j in range(1, child_max + 1):
                        if dp[v][j][0] == -1:
                            continue

                        # 合并分支选项
                        merged_k = i + j - 1
                        if merged_k <= max_m:
                            total_win = dp[u][i][0] + dp[v][j][0]
                            total_sum = dp[u][i][1] + dp[v][j][1]
                            if (total_win > ndp[merged_k][0]) or \
                               (total_win == ndp[merged_k][0] and total_sum > ndp[merged_k][1]):
                                ndp[merged_k] = (total_win, total_sum)

                        # 独立分支选项
                        separate_k = i + j
                        if separate_k <= max_m:
                            add_win = 1 if dp[v][j][1] > 0 else 0
                            total_win = dp[u][i][0] + dp[v][j][0] + add_win
                            total_sum = dp[u][i][1]
                            if (total_win > ndp[separate_k][0]) or \
                               (total_win == ndp[separate_k][0] and total_sum > ndp[separate_k][1]):
                                ndp[separate_k] = (total_win, total_sum)

                # 更新状态数组
                for k in range(len(ndp)):
                    if k > max_m:
                        continue
                    if ndp[k][0] > dp[u][k][0] or \
                       (ndp[k][0] == dp[u][k][0] and ndp[k][1] > dp[u][k][1]):
                        dp[u][k] = ndp[k]
                sz[u] += sz[v]

        dfs(-1, 0)
        max_win, sum_total = dp[0][m]

        # 处理根节点的剩余值
        if sum_total > 0:
            max_win += 1
        return max(max_win, 0)  # 保证非负
