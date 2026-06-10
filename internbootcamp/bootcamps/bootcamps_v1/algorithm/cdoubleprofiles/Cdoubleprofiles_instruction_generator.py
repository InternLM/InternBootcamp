import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from itertools import combinations
from collections import defaultdict
import re




class CdoubleprofilesInstructionGenerator(BaseInstructionGenerator):
    """Cdoubleprofiles Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=20):
        """
        初始化Cdoubleprofiles指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化参数，修正n的取值范围包含1
        增加参数校验确保合法案例生成
        """
        self.max_n = max(1, max_n)  # 确保max_n至少为1
        self.max_m = max(0, max_m)
    
    def case_generator(self):
        """
        生成合法谜题实例，完全覆盖n=1的边界情况
        优化边的生成逻辑，确保完全的随机性
        """
        n = random.randint(1, self.max_n)  # 修复n的取值范围
        max_possible_edges = n * (n - 1) // 2
        m = random.randint(0, min(self.max_m, max_possible_edges))
        
        # 生成所有可能的无向边并随机选取
        all_edges = list(combinations(range(1, n+1), 2))
        selected_edges = random.sample(all_edges, m) if m > 0 else []
        selected_edges = sorted([tuple(sorted(e)) for e in selected_edges])  # 标准化边格式
        
        correct_answer = self.compute_answer(n, m, selected_edges)
        return {
            "n": n,
            "m": m,
            "edges": selected_edges,
            "correct_answer": correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        增强问题描述规范，明确边界条件
        增加输入输出样例的规范说明
        """
        n = question_case['n']
        m = question_case['m']
        edges = question_case['edges']
        input_lines = [f"{n} {m}"] 
        input_lines += [f"{v} {u}" for v, u in sorted(edges)]
        input_str = '\n'.join(input_lines)
        
        prompt = f"""You are working at a social network company and need to find profile doubles. Two profiles i and j are doubles if for any other profile k ≠ i,j: 
- k is friends with both i and j OR 
- k is friends with neither i nor j

Rules:
1. Profiles are numbered 1..n
2. Friendship is mutual
3. Pairs (i,j) and (j,i) count as the same pair
4. n can be 1 (then answer is 0)

Input Format:
- First line: n m
- Next m lines: pairs of friends

Output Format:
- Single integer: number of valid doubles pairs

Example Input 1:
3 3
1 2
2 3
1 3

Example Output 1:
3

Current Input:
{input_str}

Present the final integer answer between [answer] and [/answer] tags."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_answer(n, m, edges):
        """
        改进哈希计算逻辑，增加对大数的容错处理
        使用更安全的模运算防止数值溢出
        """
        MOD = 10**18 + 3  # 大素数防止哈希碰撞
        B = 37

        p = [1] * (n + 2)  # 扩展数组长度防止越界
        for i in range(1, n+2):
            p[i] = (p[i-1] * B) % MOD

        h = [0] * (n + 2)
        for v, u in edges:
            h[v] = (h[v] + p[u]) % MOD
            h[u] = (h[u] + p[v]) % MOD

        m1 = defaultdict(int)
        m2 = defaultdict(int)
        for i in range(1, n+1):
            m1[h[i]] += 1
            m2[(h[i] + p[i]) % MOD] += 1  # 增加模运算

        ans = 0
        for cnt in m1.values():
            ans += cnt * (cnt - 1) // 2
        for cnt in m2.values():
            ans += cnt * (cnt - 1) // 2
        return ans
