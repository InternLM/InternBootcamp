import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_query(s, l, r):
    if l > r:
        return (0, 0, 0)
    if l == r:
        if s[l] == '(':
            return (0, 1, 0)
        else:
            return (0, 0, 1)
    mid = (l + r) // 2
    left_c, left_f, left_s = compute_query(s, l, mid)
    right_c, right_f, right_s = compute_query(s, mid + 1, r)
    extra = min(left_f, right_s)
    c = left_c + right_c + extra
    f = left_f + right_f - extra
    s_total = left_s + right_s - extra
    return (c, f, s_total)


class EserejaandbracketsRewardCalculator(BaseRewardCalculator):
    """Eserejaandbrackets奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        answers = []
        for line in last_answer.split('\n'):
            line = line.strip()
            if line:
                try:
                    answers.append(int(line))
                except ValueError:
                    pass
        return answers if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not isinstance(solution, list):
            return False
        s = identity['s']
        queries = identity['queries']
        if len(solution) != len(queries):
            return False

        for idx, (l, r) in enumerate(queries):
            l0 = l - 1
            r0 = r - 1
            if l0 < 0 or r0 >= len(s):
                correct = 0
            else:
                c, _, _ = compute_query(s, l0, r0)
                correct = c * 2
            if solution[idx] != correct:
                return False
        return True
    
    # 其他额外方法

