import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def solve(n, q, t, a_list, constraints):
    """完整实现的解题算法"""
    # 初始化图结构
    g = [[] for _ in range(n+1)]
    in_degree = [0]*(n+1)
    for u, v in constraints:
        g[u].append(v)
        in_degree[v] += 1

    # 拓扑排序检测环
    queue = deque()
    topo_order = []
    for u in range(1, n+1):
        if in_degree[u] == 0:
            queue.append(u)
    
    while queue:
        u = queue.popleft()
        topo_order.append(u)
        for v in g[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    
    if len(topo_order) != n:
        return 0  # 存在环

    # 计算依赖关系和最小金额
    dep = [0]*(n+1)
    sum_ = [0]*(n+1)
    for u in reversed(topo_order):
        sum_[u] = a_list[u-1]
        max_child_dep = 0
        for v in g[u]:
            sum_[u] += sum_[v]
            if dep[v] > max_child_dep:
                max_child_dep = dep[v]
        dep[u] = max_child_dep + 1

    min_t = sum(a_list[u-1] * dep[u] for u in topo_order)
    if t < min_t:
        return 0

    # 动态规划计算组合数
    target = t - min_t
    dp = [0]*(target+1)
    dp[0] = 1
    for u in topo_order:
        s = sum_[u]
        for j in range(s, target+1):
            dp[j] = (dp[j] + dp[j - s]) % MOD
    
    return dp[target] % MOD if target >=0 else 0


class CcointroublesRewardCalculator(BaseRewardCalculator):
    """Ccointroubles奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """加强的答案提取"""
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) % MOD if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """改进的验证逻辑"""
        try:
            expected = identity['correct_answer']
            return (int(solution) % MOD) == (expected % MOD)
        except:
            return False
    
    # 其他额外方法

