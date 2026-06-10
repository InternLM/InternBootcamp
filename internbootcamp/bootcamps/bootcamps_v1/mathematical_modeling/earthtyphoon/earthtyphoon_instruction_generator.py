import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class EarthtyphoonInstructionGenerator(BaseInstructionGenerator):
    """Earthtyphoon Bootcamp指令生成器"""
    
    def __init__(self, v_range=(0, 100), seed=None):
        """
        初始化Earthtyphoon指令生成器
        
        Args:
            v_range: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.v_range = v_range
        if seed is not None:
            np.random.seed(seed)
    
    def case_generator(self):
        # 1. 随机采样参数 v
        v = float(np.random.uniform(*self.v_range))
        mslp = 1021.36 - 0.36*v - (v/20.16)**2
        return {"v": v, "mslp": mslp}
    
    def prompt_func(self, identity) -> str:
        v = identity["v"]
        return (
            f"下面给出最大风速（v）={v} (kt)\n\n"
            "请计算平均海平面气压（单位是 百帕 hPa），计算公式为：\n"
            "mslp = 1021.36 - 0.36*v - (v/20.16)**2\n"
            "请将最终计算结果放入\\boxed{}中，例如：\\boxed{1234.56}"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

