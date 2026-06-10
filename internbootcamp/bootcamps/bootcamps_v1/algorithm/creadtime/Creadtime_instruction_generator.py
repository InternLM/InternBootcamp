import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from math import inf

# === 源文件中的全局函数 ===

def calculate_min_time(n, m, h, p):
    h = sorted(h)
    p = sorted(p)
    ss = 0
    ll = 2 * 10**18  # A sufficiently large upper bound

    while ss < ll:
        avg = (ss + ll) // 2
        works = True
        hidx = 0
        pidx = 0

        while hidx < n and pidx < m:
            current_p = p[pidx]
            current_h = h[hidx]

            if current_h - current_p > avg:
                works = False
                break

            # Calculate the furthest right track covered
            getback_time = max(0, 2 * (current_h - current_p))
            also_to_right = max(0, avg - getback_time)
            left_time = max(0, current_h - current_p)
            remaining_time = max(0, (avg - left_time) // 2)
            furthest_right = current_h + max(also_to_right, remaining_time)

            # Move to the first p not covered by current head
            while pidx < m and p[pidx] <= furthest_right:
                pidx += 1

            hidx += 1

        if pidx < m:
            works = False

        if works:
            ll = avg
        else:
            ss = avg + 1

    return ss


class CreadtimeInstructionGenerator(BaseInstructionGenerator):
    """Creadtime Bootcamp指令生成器"""
    
    def __init__(self, n_range=(1, 5), m_range=(1, 5), h_max=1000, p_max=10000):
        """
        初始化Creadtime指令生成器
        
        Args:
            n_range: 参数描述
            m_range: 参数描述
            h_max: 参数描述
            p_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_range = n_range
        self.m_range = m_range
        self.h_max = h_max
        self.p_max = p_max
    
    def case_generator(self):
        n = random.randint(*self.n_range)
        m = random.randint(*self.m_range)
        
        # Generate h with sorted unique elements
        h = sorted(random.sample(range(1, self.h_max), n))
        
        # Generate p with sorted unique elements
        p = sorted(random.sample(range(1, self.p_max), m))
        
        return {
            "n": n,
            "m": m,
            "h": h,
            "p": p
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        case = question_case
        h_list = ' '.join(map(str, case['h']))
        p_list = ' '.join(map(str, case['p']))
        
        return f"""You are an AI assistant tasked with solving a hard drive head movement optimization problem. Your goal is to determine the minimal time required for all specified tracks to be read by multiple moving heads.

**Problem Rules:**
- There are {case['n']} heads initially positioned at distinct tracks in ascending order.
- You need to read {case['m']} distinct target tracks in ascending order.
- Each head can move one track left/right or stay each second. The total time is determined by the longest movement time of any head.
- All required tracks must be covered by at least one head's path during their movements.

**Input Format:**
1. First line: n m (number of heads and target tracks)
2. Second line: h1 h2 ... hn (initial head positions, sorted)
3. Third line: p1 p2 ... pm (target tracks, sorted)

**Output Format:**
A single integer - the minimal time required.

**Example:**
Input:
3 4
2 5 6
1 3 6 8
Output:
2

**Your Task:**
Given the input below, compute the minimal time required. Enclose your answer within [answer] and [/answer] tags.

Input:
{case['n']} {case['m']}
{h_list}
{p_list}

Reason step by step, then provide the final answer within [answer] tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

