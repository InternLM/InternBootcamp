import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def solve_water_tanks(input_list):
    n = len(input_list)
    if n == 0:
        return []
    l = input_list
    su = [l[0]]
    cou = [-1, 0]
    for k in range(1, n):
        nd = 1
        ns = l[k]
        while len(cou) > 1 and su[-1] * (cou[-1] - cou[-2] + nd) > (su[-1] + ns) * (cou[-1] - cou[-2]):
            nd += cou[-1] - cou[-2]
            ns += su[-1]
            su.pop()
            cou.pop()
        cou.append(k)
        su.append(ns)
    af = []
    for k in range(len(su)):
        count = cou[k+1] - cou[k]
        avg = su[k] / count
        af.extend([avg] * count)
    return af


class CwaterbalanceRewardCalculator(BaseRewardCalculator):
    """Cwaterbalance奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1]
        numbers = re.findall(r'\b\d+\.\d{9}\b', last_match)
        try:
            result = [float(num) for num in numbers]
        except:
            return None
        return result if len(result) > 0 else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['output']
        if solution is None or len(solution) != len(expected):
            return False
        for s, e in zip(solution, expected):
            if not (abs(s - e) <= 1e-9 * max(1, abs(e))):
                return False
        return True
    
    # 其他额外方法

