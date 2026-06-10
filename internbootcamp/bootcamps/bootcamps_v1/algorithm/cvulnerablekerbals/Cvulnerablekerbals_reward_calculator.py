import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class CvulnerablekerbalsRewardCalculator(BaseRewardCalculator):
    """Cvulnerablekerbals奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip()
        lines = [l.strip() for l in answer.split('\n') if l.strip()]
        if len(lines) < 2:
            return None
        try:
            k = int(lines[0])
            elements = list(map(int, lines[1].split()))
            if len(elements) != k:
                return None
            return elements
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        m = identity['m']
        forbidden = set(identity['forbidden'])
        k_max = identity['k_max']
        
        if len(solution) != k_max:
            return False
        
        for num in solution:
            if not (0 <= num < m):
                return False
        
        current = 1
        prefix_products = []
        for num in solution:
            current = (current * num) % m
            if current in forbidden or current in prefix_products:
                return False
            prefix_products.append(current)
        
        return True
    
    # 其他额外方法

