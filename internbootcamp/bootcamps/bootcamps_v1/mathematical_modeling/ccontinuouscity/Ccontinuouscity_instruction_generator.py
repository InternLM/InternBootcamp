import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Set




class CcontinuouscityInstructionGenerator(BaseInstructionGenerator):
    """Ccontinuouscity Bootcamp指令生成器"""
    
    def __init__(self, max_blocks=32):
        """
        初始化Ccontinuouscity指令生成器
        
        Args:
            max_blocks: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.max_blocks = max_blocks
    
    def case_generator(self) -> dict:
        """生成包含可能和不可能两种情况的多样化测试用例"""
        # 50% 概率生成可解决的案例
        if random.random() < 0.5:
            L = random.randint(1, 100)
            R = L + random.randint(0, 100)
            success, structure = self.construct_valid_structure(L, R)
        else:
            # 生成不可能的情况（例如过大的区间）
            L = random.randint(1, 100)
            R = L + 10**6 + 1  # 确保无法满足
            success = False
        
        return {
            'L': L,
            'R': R,
            'possible': success,
            'structure': structure if success else None
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        L, R = question_case['L'], question_case['R']
        return f"""Determine if an (L,R)-continuous city exists with L={L}, R={R} and ≤32 blocks.

Requirements:
1. All 1→n path lengths must be in [{L}, {R}]
2. Each integer in [{L}, {R}] has exactly one path

Output format:
If possible:
YES
n m
a1 b1 c1
...
am bm cm

If impossible:
NO

Place your final answer between [answer] and [/answer] tags exactly as shown.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def construct_valid_structure(self, L: int, R: int) -> Tuple[bool, Optional[Dict]]:
        """实现完整的结构构造逻辑"""
        n = 32
        edges = []
        cl = [0] * (n-1)
        cr = [1] * (n-1)

        # 初始化第一个块
        edges.append((1, n, L))
        current_L = L + 1

        for vi in range(1, 30):  # 构造中间块
            if current_L > R:
                break

            max_step = min(1 << (vi-1), R - current_L + 1)
            if max_step <= 0:
                break

            cl[vi] = cr[vi-1]
            cr[vi] = cl[vi]

            # 连接所有之前的块
            for j in range(vi-1, -1, -1):
                delta = cr[j] - cl[j]
                if cr[vi] + delta <= cl[vi] + max_step:
                    edges.append((j+1, vi+1, cr[vi] - cl[j]))
                    cr[vi] += delta

            # 添加到终点的边
            edge_weight = current_L - cl[vi]
            edges.append((vi+1, n, edge_weight))
            current_L += max_step

        if current_L - 1 < R:
            return False, None

        return True, {
            'n': n,
            'm': len(edges),
            'edges': edges
        }

    @staticmethod
    def validate_paths(n: int, edges: List[Tuple[int,int,int]], L: int, R: int) -> bool:
        """优化的路径验证算法"""
        # 构建邻接表
        adj = [[] for _ in range(n+1)]
        edge_map = {}
        for a, b, c in edges:
            adj[a].append((b, c))
            edge_map[(a,b)] = c

        # 使用动态规划计算所有路径长度
        dp = [set() for _ in range(n+1)]
        dp[1].add(0)

        for u in range(1, n+1):
            if not dp[u]:
                continue
            for v, w in adj[u]:
                dp[v].update({path_len + w for path_len in dp[u]})

        all_lengths = dp[n]
        if not all_lengths:
            return False

        # 检查范围
        min_len = min(all_lengths)
        max_len = max(all_lengths)
        if min_len != L or max_len != R:
            return False

        # 检查连续性和唯一性
        expected = set(range(L, R+1))
        return all_lengths == expected
