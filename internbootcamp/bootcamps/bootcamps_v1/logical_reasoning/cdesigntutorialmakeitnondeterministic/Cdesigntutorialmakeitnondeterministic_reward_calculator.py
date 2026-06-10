import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def solve_handle_order(names, p_list):
    if not names or len(p_list) != len(names):
        return "NO"
    n = len(names)
    p = p_list
    Flag = True
    current_user = names[p[0]-1]
    a, b = current_user
    Tmp = a if a < b else b
    for i in range(1, len(p)):
        current_user = names[p[i]-1]
        a, b = current_user
        current_min = a if a < b else b
        current_max = b if a < b else a
        if Tmp >= current_min:
            if Tmp >= current_max:
                Flag = False
                break
            else:
                Tmp = current_max
        else:
            Tmp = current_min
    return "YES" if Flag else "NO"

def generate_random_string(min_length=1, max_length=50):
    length = random.randint(min_length, max_length)
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length))


class CdesigntutorialmakeitnondeterministicRewardCalculator(BaseRewardCalculator):
    """Cdesigntutorialmakeitnondeterministic奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 支持多格式匹配（包含换行和大小写）
        matches = re.findall(r'\[answer\s*\]\s*(.*?)\s*\[\s*/answer\s*\]', output, re.IGNORECASE | re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip().upper()
        return last_match if last_match in {"YES", "NO"} else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 验证前先进行基本清洗
        cleaned_solution = str(solution).strip().upper()
        return cleaned_solution == solve_handle_order(identity['names'], identity['p'])
    
    # 其他额外方法

