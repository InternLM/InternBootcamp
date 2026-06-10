from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
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


class CunclebogdanandcountryhappinessInteraction(BaseInteraction):
    """Cunclebogdanandcountryhappiness交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = CunclebogdanandcountryhappinessRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cunclebogdanandcountryhappiness问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
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
