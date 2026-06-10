import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import math
import random

# === 源文件中的全局函数 ===

def remove_boxed(s):
    if "\\boxed " in s:
        left = "\\boxed "
        assert s[:len(left)] == left
        return s[len(left):]

    left = "\\boxed{"

    assert s[:len(left)] == left
    assert s[-1] == "}"

    return s[len(left):-1]

def last_boxed_only_string(string):
    idx = string.rfind("\\boxed")
    if "\\boxed " in string:
        return "\\boxed " + string.split("\\boxed ")[-1].split("$")[0]
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1

    if right_brace_idx is None:
        retval = None
    else:
        retval = string[idx:right_brace_idx + 1]

    return retval


class MedcalculatorRewardCalculator(BaseRewardCalculator):
    """Medcalculator奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        output = last_boxed_only_string(output)
        if output is None:
            return None
        return remove_boxed(output)
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if ':' in solution:
            solution = solution.split(':')[-1].strip()
        elif '：' in solution:
            solution = solution.split('：')[-1].strip()

        return solution.strip() == str(identity['target'])
    
    # 其他额外方法

