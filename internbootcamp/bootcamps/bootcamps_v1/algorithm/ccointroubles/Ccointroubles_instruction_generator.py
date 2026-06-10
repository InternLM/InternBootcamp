import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class CcointroublesInstructionGenerator(BaseInstructionGenerator):
    """Ccointroubles Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_q=3, max_a=5, max_t=1000):
        """
        初始化Ccointroubles指令生成器
        
        Args:
            max_n: 参数描述
            max_q: 参数描述
            max_a: 参数描述
            max_t: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_q = max_q
        self.max_a = max_a
        self.max_t = max_t
    
    def case_generator(self):
        """改进的测试用例生成器"""
        for _ in range(100):  # 最多尝试次数
            # 生成有效约束条件
            n = random.randint(1, self.max_n)
            a = [random.randint(1, self.max_a) for _ in range(n)]
            
            # 生成拓扑约束
            nodes = list(range(1, n+1))
            random.shuffle(nodes)
            constraints = []
            used_bi = set()
            used_ci = set()
            
            # 保证bi/ci唯一的有效生成方式
            available_bi = nodes.copy()
            available_ci = nodes.copy()
            for _ in range(min(self.max_q, n//2)):
                if not available_bi or not available_ci:
                    break
                bi = random.choice(available_bi)
                available_bi.remove(bi)
                ci_candidates = [c for c in available_ci if c != bi and c not in used_ci]
                if not ci_candidates:
                    continue
                ci = random.choice(ci_candidates)
                available_ci.remove(ci)
                constraints.append((bi, ci))
                used_bi.add(bi)
                used_ci.add(ci)
            
            q = len(constraints)
            
            # 计算最小金额
            min_t = self._calculate_min_t(n, a, constraints)
            if min_t is None or min_t > self.max_t:
                continue
            
            # 生成有效金额
            max_add = self.max_t - min_t
            t = min_t + random.randint(0, max(0, max_add))
            
            # 验证案例有效性
            case = {
                'n': n,
                'q': q,
                't': t,
                'a': a.copy(),
                'constraints': constraints.copy()
            }
            
            # 计算标准答案
            try:
                ans = solve(n, q, t, a, constraints)
                if ans >= 0:
                    case['correct_answer'] = ans
                    return case
            except:
                continue
        return None  # 极端情况下返回空
    
    @staticmethod
    def prompt_func(case):
        """优化的问题描述生成"""
        constraints = "\n".join([f"- Type {b} coins > Type {c} coins" 
                               for b, c in case['constraints']])
        return f"""Calculate valid coin combinations with:
- {case['n']} coin types: {', '.join(map(str, case['a']))}
- Total required: {case['t']} cents
- Constraints:
{constraints}

Output the answer modulo 1e9+7 within [answer]...[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _calculate_min_t(self, n, a, constraints):
        """辅助函数：计算最小金额"""
        try:
            temp_g = [[] for _ in range(n+1)]
            for u, v in constraints:
                temp_g[u].append(v)

            # 计算拓扑深度
            depth = [0]*(n+1)
            for u in range(n, 0, -1):
                max_child = 0
                for v in temp_g[u]:
                    max_child = max(max_child, depth[v])
                depth[u] = max_child + 1

            return sum(a[u-1] * depth[u] for u in range(1, n+1))
        except:
            return None
