import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answers(n, a, queries):
    aa = a.copy()
    m = len(queries)
    res = []
    
    if n == 0:
        return [0] * m  # Only one element, no possible inversions
    
    if n < 2:
        a1, a2 = aa[0], aa[1]
        original_inversion = 1 if a1 > a2 else 0
        reversed_inversion = 1 if a2 > a1 else 0
        current_inversion = original_inversion
        f = False  # Tracks whether the array is reversed
        for q in queries:
            if q != 0:
                f = not f
                current_inversion = reversed_inversion if f else original_inversion
            res.append(current_inversion)
        return res
    
    n2 = 2 ** n
    acc0 = []
    acc1 = []
    
    # Initialize for q=1 and q=2 levels
    a00 = a01 = a10 = a11 = 0
    for i in range(0, n2, 4):
        a_val = aa[i]
        b_val = aa[i+1] if i+1 < n2 else 0
        c_val = aa[i+2] if i+2 < n2 else 0
        d_val = aa[i+3] if i+3 < n2 else 0
        
        a00 += (b_val < a_val) + (d_val < c_val)
        a01 += (c_val < a_val) + (c_val < b_val) + (d_val < a_val) + (d_val < b_val)
        a10 += (b_val > a_val) + (d_val > c_val)
        a11 += (c_val > a_val) + (c_val > b_val) + (d_val > a_val) + (d_val > b_val)
    
    acc0 = [a00, a01]
    acc1 = [a10, a11]
    w = 4
    
    while w < n2:
        a00 = 0
        a10 = 0
        for i in range(0, n2, w * 2):
            le = sorted(aa[i:i + w])
            ri = sorted(aa[i + w:i + w * 2])
            
            # Compute a00 (inversions from left to right)
            i_le, j_ri, cnt = 0, 0, 0
            while i_le < len(le) and j_ri < len(ri):
                if le[i_le] > ri[j_ri]:
                    j_ri += 1
                else:
                    cnt += j_ri
                    i_le += 1
            cnt += j_ri * (len(le) - i_le)
            a00 += cnt
            
            # Compute a10 (inversions from right to left)
            i_ri, j_le, cnt = 0, 0, 0
            while i_ri < len(ri) and j_le < len(le):
                if ri[i_ri] > le[j_le]:
                    j_le += 1
                else:
                    cnt += j_le
                    i_ri += 1
            cnt += j_le * (len(ri) - i_ri)
            a10 += cnt
        
        acc0.append(a00)
        acc1.append(a10)
        w *= 2
    
    # Handling queries by swapping acc0 and acc1 as needed
    for q in queries:
        current_q = q
        # Flip all levels up to q
        for level in range(current_q):
            if level < len(acc0):
                acc0[level], acc1[level] = acc1[level], acc0[level]
        res.append(sum(acc0))
        # Restore original state for next query
        for level in range(current_q):
            if level < len(acc0):
                acc0[level], acc1[level] = acc1[level], acc0[level]
                
    return res


class CmashmokhandreverseoperationRewardCalculator(BaseRewardCalculator):
    """Cmashmokhandreverseoperation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1]
        lines = [line.strip() for line in last_match.splitlines() if line.strip()]
        solutions = []
        for line in lines:
            try:
                solutions.append(int(line))
            except ValueError:
                continue
        return solutions if solutions else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity.get('expected_outputs', [])
        if not isinstance(solution, list) or len(solution) != len(expected):
            return False
        return all(s == e for s, e in zip(solution, expected))
    
    # 其他额外方法

