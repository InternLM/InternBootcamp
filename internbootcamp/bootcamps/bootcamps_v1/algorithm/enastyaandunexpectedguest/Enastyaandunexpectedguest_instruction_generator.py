import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def correct_solution(n, m, d, g, r):
    d_sorted = sorted(d)
    # Check if any adjacent islands exceed g distance
    for i in range(1, len(d_sorted)):
        if d_sorted[i] - d_sorted[i-1] > g:
            return -1
    m = len(d_sorted)
    INF = float('inf')
    dp = [[INF] * (g + 1) for _ in range(m)]
    dp[0][0] = 0
    heap = []
    import heapq
    heapq.heappush(heap, (0, 0, 0))  # (cycles, u, rem)

    while heap:
        cycles, u, rem = heapq.heappop(heap)
        if cycles > dp[u][rem]:
            continue
        for dv in [-1, 1]:
            v = u + dv
            if 0 <= v < m:
                distance = abs(d_sorted[u] - d_sorted[v])
                new_rem = rem + distance
                if new_rem > g:
                    continue
                if new_rem == g:
                    new_cycles = cycles + 1
                    new_r = 0
                else:
                    new_cycles = cycles
                    new_r = new_rem
                if dp[v][new_r] > new_cycles:
                    dp[v][new_r] = new_cycles
                    heapq.heappush(heap, (new_cycles, v, new_r))
    min_time = INF
    for i in range(m):
        time_needed = n - d_sorted[i]
        if time_needed <= g and dp[i][0] != INF:
            total_time = dp[i][0] * (g + r) + time_needed
            if total_time < min_time:
                min_time = total_time
    return min_time if min_time != INF else -1


class EnastyaandunexpectedguestInstructionGenerator(BaseInstructionGenerator):
    """Enastyaandunexpectedguest Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Enastyaandunexpectedguest指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'n_range': (1, 100),
            'm_range_low': 2,
            'm_range_high': 100,
            'g_range': (1, 1000),
            'r_range': (1, 1000),
        }
        self.params.update(params)
    
    def case_generator(self):
        n = random.randint(*self.params['n_range'])
        m_high = min(n + 1, self.params['m_range_high'])
        m = random.randint(self.params['m_range_low'], m_high)
        d = [0, n]
        while len(d) < m:
            new_point = random.randint(0, n)
            if new_point not in d:
                d.append(new_point)
        d = sorted(d)
        # Allow g to be smaller than gaps to generate impossible cases
        g = random.randint(*self.params['g_range'])
        r = random.randint(*self.params['r_range'])
        return {
            'n': n,
            'm': m,
            'd': d,
            'g': g,
            'r': r,
        }
    
    @staticmethod
    def prompt_func(question_case):
        case = question_case
        d_str = ' '.join(map(str, case['d']))
        prompt = f"""你是编程竞赛选手，需要解决以下问题。请仔细阅读问题描述并按要求输出答案。

问题描述：
Enastyaandunexpectedguest必须穿过一条宽为{case['n']}米的马路。马路的安全岛位于多个坐标点，包括0米和{case['n']}米。交通灯先绿{case['g']}秒，后红{case['r']}秒，反复循环。Enastyaandunexpectedguest从坐标0出发，必须在绿灯期间移动，每秒移动±1米，且只能在安全岛改变方向。红灯期间必须停留在安全岛。求到达坐标{case['n']}的最短时间，若不可能输出-1。

输入格式：
第一行包含两个整数n和m：{case['n']} {case['m']}
第二行包含{case['m']}个不同的整数，按递增顺序排列：{d_str}
第三行包含两个整数g和r：{case['g']} {case['r']}

输出格式：
输出一个整数，表示最短时间或-1。

请将你的答案放置在[answer]标签内。例如：[answer]45[/answer] 或 [answer]-1[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

