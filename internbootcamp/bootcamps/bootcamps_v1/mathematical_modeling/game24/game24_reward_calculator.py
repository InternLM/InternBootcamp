import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import json
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.game24.lib.libs import Game24Plus

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


class Game24RewardCalculator(BaseRewardCalculator):
    """Game24奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        Extract the output from the solution.
        
        Args:
            output: Model output to be processed.
        
        Returns:
            The processed output.
        """
        output = last_boxed_only_string(output)
        if output is None:
            return None
        return remove_boxed(output)
    
    @classmethod 
    def _verify_correction(cls, solution, identity)->bool:
        """
        Verify the correction of the solution.
        """ 
        puzzle, target = identity['puzzle'], identity['target']
        current_numbers = puzzle.split()
        solution = cls._normalize_solution(solution)
        # 提取所有数字
        numbers = re.findall(r'\d+', solution)
        # 提取所有运算符
        operators = re.findall(r'[+\-*/]', solution)
        
        # 检查数字
        if len(numbers) != len(current_numbers):
            return False
        for n in numbers:
            if n not in current_numbers:
                return False
            current_numbers.remove(n)
        if current_numbers:
            return False
        # 检查运算符
        if '**' in solution or '//' in solution:
            return False
        if any(op not in '+-*/' for op in operators):
            return False
        
        try:
            # 计算结果
            result = eval(solution)
            if result != int(target):
                return False
        except:
            return False
        
        return True
    
    # 其他额外方法

