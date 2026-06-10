import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def solve_case(n_input, k_input):
    MAX_PRECOMPUTE = 100
    f = [0]
    for _ in range(MAX_PRECOMPUTE):
        f.append(f[-1] * 4 + 1)
    p = [0]
    for g in range(MAX_PRECOMPUTE):
        p.append(p[-1] + (2 ** (g + 1) - 1))
    
    n, k = n_input, k_input

    if k == 1:
        return f"YES {n-1}"
    
    # 计算最大可能的分割次数（不考虑路径条件）
    max_f = (4**n - 1) // 3
    if k > max_f:
        return "NO"
    
    original_n = n
    
    # 直接遍历所有可能的j（不截断n）
    for j in range(original_n - 1, -1, -1):
        m_segment = original_n - j
        
        # 计算当前段的p值
        if m_segment < len(p):
            current_p = p[m_segment]
        else:
            current_p = 2 * (2**m_segment - 1) - m_segment
        
        if current_p > k:
            continue
        
        # 计算剩余可用分割次数
        other = 2 ** m_segment
        if j < len(f):
            f_j = f[j]
        else:
            f_j = (4**j - 1) // 3
        
        avail = (other - 1) ** 2 * f_j
        
        # 判断是否满足总分割次数
        if current_p + avail >= k:
            answer_m = original_n - m_segment
            return f"YES {answer_m}"
    
    return "NO"


class DolyaandmagicalsquareRewardCalculator(BaseRewardCalculator):
    """Dolyaandmagicalsquare奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL | re.IGNORECASE)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = solve_case(identity['n'], identity['k'])
        processed_sol = ' '.join(solution.strip().split()).upper()
        processed_exp = ' '.join(expected.strip().split()).upper()
        return processed_sol == processed_exp
    
    # 其他额外方法

