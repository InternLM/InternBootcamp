import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def evaluate_expression(numbers, operators):
    nums = numbers.copy()
    ops = operators.copy()
    
    # 处理乘除运算
    i = 0
    while i < len(ops):
        if ops[i] in ('*', '/'):
            a = nums[i]
            b = nums[i+1]
            try:
                if ops[i] == '*':
                    res = a * b
                else:
                    res = a // b if b != 0 else 0
                nums[i] = res
                del nums[i+1]
                del ops[i]
            except:
                return None
        else:
            i += 1
    
    # 处理加减运算
    try:
        result = nums[0]
        for i in range(len(ops)):
            if ops[i] == '+':
                result += nums[i+1]
            else:
                result -= nums[i+1]
        return result
    except:
        return None


class KorpuzzlemathpathRewardCalculator(BaseRewardCalculator):
    """Korpuzzlemathpath奖励计算器"""
    
    @staticmethod  # 修正此处缩进
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1] if matches else None
    
    @classmethod  # 修正此处缩进
    def _verify_correction(cls, solution, identity):
        try:
            if '=' not in solution:
                return False
            left, right = solution.split('=', 1)
            target = int(right.strip())
            if target != identity['target']:
                return False
            
            tokens = re.findall(r'(\d+|\+|\-|\*|/)', left)
            if len(tokens) < 1 or len(tokens) % 2 == 0:
                return False
            
            numbers = []
            operators = []
            for i, token in enumerate(tokens):
                if i % 2 == 0:
                    if not token.isdigit():
                        return False
                    num = int(token)
                    if num < 0 or num > 9:
                        return False
                    numbers.append(num)
                else:
                    operators.append(token)
            
            if len(operators) != len(identity['operators']):
                return False
            for op_case, op_user in zip(identity['operators'], operators):
                if op_case != op_user:
                    return False
            
            calculated = evaluate_expression(numbers, operators)
            return calculated == identity['target']
        except:
            return False
    
    # 其他额外方法

