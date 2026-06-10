import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.cunclebogdanandcountryhappiness.Cunclebogdanandcountryhappiness_reward_calculator import CunclebogdanandcountryhappinessRewardCalculator

# 导入依赖库
import re
import random
from collections import deque

# === 源文件中的全局函数 ===

def generate_tree_edges(n):
    if n == 1:
        return []
    parents = [0] * (n + 1)  # 1-based index
    for i in range(2, n + 1):
        parents[i] = random.randint(1, i - 1)
    return [(parents[i], i) for i in range(2, n + 1)]

def generate_p(n, m):
    if m == 0:
        return [0] * n
    p = []
    remaining = m
    for _ in range(n - 1):
        val = random.randint(0, remaining)
        p.append(val)
        remaining -= val
    p.append(remaining)
    return p

def build_tree_and_parents(n, edges):
    adj = [[] for _ in range(n + 1)]  # 1-based
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent = [0] * (n + 1)
    visited = [False] * (n + 1)
    q = deque([1])
    visited[1] = True
    while q:
        u = q.popleft()
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                q.append(v)
    return parent

def dfs(graph, p, h, start=0):
    n = len(graph)
    dp = [[0, 0] for _ in range(n)]
    visited, finished = [False]*n, [False]*n
    stack = [start]
    while stack:
        curr = stack[-1]
        if not visited[curr]:
            visited[curr] = True
            for child in graph[curr]:
                if not visited[child]:
                    stack.append(child)
        else:
            curr = stack.pop()
            dp[curr][0] = p[curr]
            dp[curr][1] = 0
            for child in graph[curr]:
                if finished[child]:
                    dp[curr][0] += dp[child][0]
                    dp[curr][1] += dp[child][1]
            lower = dp[curr][1] - dp[curr][0]
            upper = dp[curr][1] + dp[curr][0]
            if not (lower <= h[curr] <= upper and (h[curr] - lower) % 2 == 0):
                return False
            v = (h[curr] - lower) // 2
            dp[curr][1] += v
            dp[curr][0] -= v
            finished[curr] = True
    return True

def main():
    t = int(input())
    for _ in range(t):
        n, m = map(int, input().split())
        p = list(map(int, input().split()))
        h = list(map(int, input().split()))
        graph = [[] for _ in range(n)]
        for _ in range(n-1):
            x, y = map(int, input().split())
            x -= 1; y -= 1
            graph[x].append(y); graph[y].append(x)
        tree = [[] for _ in range(n)]
        visited = [False]*n
        stack = [0]
        while stack:
            curr = stack.pop()
            visited[curr] = True
            for child in graph[curr]:
                if not visited[child]:
                    tree[curr].append(child)
                    stack.append(child)
        print("YES" if dfs(tree, p, h) else "NO")

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CunclebogdanandcountryhappinessVerificationTool(BaseTool):
    """Cunclebogdanandcountryhappiness验证工具"""
    
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
            score = CunclebogdanandcountryhappinessRewardCalculator.verify_score(
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
            logger.error(f"CunclebogdanandcountryhappinessVerificationTool执行错误: {str(e)}")
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
    def solve_happiness(self, input_str):
        from io import StringIO
        import sys
        old_stdin = sys.stdin
        sys.stdin = StringIO(input_str)
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        main()

        output = sys.stdout.getvalue().strip().upper()
        sys.stdin = old_stdin
        sys.stdout = old_stdout
        return output == 'YES'
