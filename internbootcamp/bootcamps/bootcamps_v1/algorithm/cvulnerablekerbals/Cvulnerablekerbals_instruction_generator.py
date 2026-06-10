import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import math
import random
from collections import defaultdict

# === 源文件中的全局函数 ===

def exgcd(a, b):
    if b == 0:
        return (a, 1, 0)
    else:
        g, x, y = exgcd(b, a % b)
        return (g, y, x - (a // b) * y)

def generate_solution_for_m(m):
    vis = set()
    g = defaultdict(list)
    for i in range(m):
        if i not in vis:
            g_val = math.gcd(i, m)
            g[g_val].append(i)
    
    divisors = [d for d in range(1, m + 1) if m % d == 0]
    divisors.sort()
    
    dp = {d: 0 for d in divisors}
    pre = {d: None for d in divisors}
    
    for d in divisors:
        dp[d] = len(g.get(d, []))
        j = 2 * d
        while j <= m:
            if j not in divisors:
                j += d
                continue
            if dp[j] < dp[d]:
                dp[j] = dp[d]
                pre[j] = d
            elif dp[j] == dp[d]:
                if pre[j] is None or pre[j] < d:
                    pre[j] = d
            j += d
    
    current_d = m
    w = []
    while True:
        w.extend(g.get(current_d, []))
        if current_d == 1:
            break
        current_d = pre.get(current_d)
        if current_d is None:
            break
    
    if not w:
        return 0, []
    
    sequence = []
    sequence.append(w[-1])
    for i in range(len(w)-1, 0, -1):
        a = w[i]
        b = w[i-1]
        g_val, x, y = exgcd(a, m)
        assert b % g_val == 0, "No solution"
        x0 = (x * (b // g_val)) % (m // g_val)
        sequence.append(x0)
    
    current = 1
    prefix_products = []
    for num in sequence:
        current = (current * num) % m
        prefix_products.append(current)
    
    return len(sequence), prefix_products


class CvulnerablekerbalsInstructionGenerator(BaseInstructionGenerator):
    """Cvulnerablekerbals Bootcamp指令生成器"""
    
    def __init__(self, m_min=2, m_max=20):
        """
        初始化Cvulnerablekerbals指令生成器
        
        Args:
            m_min: 参数描述
            m_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.m_min = m_min
        self.m_max = m_max
    
    def case_generator(self):
        m = random.randint(self.m_min, self.m_max)
        k_max, P = generate_solution_for_m(m)
        all_numbers = set(range(m))
        P_set = set(P)
        C = list(all_numbers - P_set)
        max_n = min(len(C), m-1)
        n = random.randint(0, max_n) if max_n >= 0 else 0
        L = random.sample(C, n) if n > 0 else []
        L.sort()
        return {
            'm': m,
            'n': n,
            'forbidden': L,
            'k_max': k_max
        }
    
    @staticmethod
    def prompt_func(question_case):
        m = question_case['m']
        n = question_case['n']
        forbidden = question_case['forbidden']
        problem = f"You are given an integer m and a list of n distinct integers between 0 and m-1.\n\n"
        problem += "Your task is to construct a sequence satisfying the following properties:\n"
        problem += "1. Each element is an integer between 0 and m-1, inclusive.\n"
        problem += "2. All prefix products of the sequence modulo m are distinct.\n"
        problem += "3. No prefix product modulo m appears in the forbidden list.\n"
        problem += "4. The length of the sequence is maximized.\n\n"
        problem += "Input:\n"
        problem += f"{n} {m}\n"
        if n > 0:
            problem += " ".join(map(str, forbidden)) + "\n"
        problem += "\nOutput your answer in the following format:\n"
        problem += "[answer]\n<length>\n<sequence elements space-separated>\n[/answer]"
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

