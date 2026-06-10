import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def calculate_solution(n, messages):
    entered = set()
    prefix = []
    for sign, num in messages:
        if sign == '+':
            entered.add(num)
        else:
            if num not in entered:
                prefix.append(('+', num))
    prefix.reverse()
    full_messages = prefix + messages
    online = set()
    leaders = set(range(1, n+1))
    prev_sign = None
    prev_num = 0
    
    for m in full_messages:
        sign, num = m
        if prev_sign is not None and prev_sign != sign and prev_num != num:
            if num in leaders:
                leaders.remove(num)
            if prev_num in leaders:
                leaders.remove(prev_num)
        if sign == '+':
            if len(online) > 0 and num in leaders:
                leaders.remove(num)
            online.add(num)
        else:
            if num in online:
                online.remove(num)
            if len(online) > 0 and num in leaders:
                leaders.remove(num)
        prev_sign, prev_num = sign, num
    return sorted(leaders) if leaders else []


class ConlinemeetingRewardCalculator(BaseRewardCalculator):
    """Conlinemeeting奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            return None
        
        try:
            k = int(lines[0])
        except:
            return None
        
        if k == 0:
            return 0 if len(lines) == 1 else None
        else:
            if len(lines) < 2:
                return None
            try:
                leaders = list(map(int, lines[1].split()))
            except:
                return None
            if len(leaders) != k or sorted(leaders) != leaders:
                return None
            return leaders
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['expected_leaders']
        if solution == 0:
            return len(expected) == 0
        elif isinstance(solution, list):
            return solution == expected
        else:
            return False
    
    # 其他额外方法

