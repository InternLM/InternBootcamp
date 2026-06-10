import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import json
import numpy as np

# === 源文件中的全局函数 ===

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

def remove_boxed(s):
    if "\\boxed " in s:
        left = "\\boxed "
        assert s[:len(left)] == left
        return s[len(left):]

    left = "\\boxed{"

    assert s[:len(left)] == left
    assert s[-1] == "}"

    return s[len(left):-1]


class EarthtyphoonRewardCalculator(BaseRewardCalculator):
    """Earthtyphoon奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> str:
        # 用正则提取“mslp = …”右侧的表达式
        output = last_boxed_only_string(output)
        if output is None:
            return ""
        return remove_boxed(output)
    
    @classmethod
    def _verify_correction(cls, solution: str, identity: dict) -> bool:
        # 解析 LLM 给出的系数 c，形如 “c*x”
        solution = solution.replace(" ", "")
        try:
            c = float(solution)
        except:
            return False
        # print(c)
        # 验证 c ≈ k
        if abs(c - identity["mslp"]) < 1e-2:
            return 1
        return 0
    
    # 其他额外方法

