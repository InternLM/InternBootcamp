import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class Game24InstructionGenerator(BaseInstructionGenerator):
    """Game24 Bootcamp指令生成器"""
    
    def __init__(self, num_numbers=4, range_max=100, target_max=100, seed = None):
        """
        初始化Game24指令生成器
        
        Args:
            num_numbers: 参数描述
            range_max: 参数描述
            target_max: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        # super.__init__()
        self.num_numbers = num_numbers
        self.range_max = range_max
        self.target_max = target_max
        self.seed = seed
        self.game24Plus = Game24Plus(num_numbers,range_max,target_max,seed)
    
    def case_generator(self) -> object:
        """
        生成一组数字和目标值。
        """
        # game24Plus = Game24Plus(num_numbers,range_max,target_max,seed)
        self.numbers = self.game24Plus.get_numbers()
        self.target, self.operations = self.game24Plus.get_target_limit_range(self.numbers)
        return {'puzzle': ' '.join(str(i) for i in self.numbers), 'target':self.target}
    
    def prompt_func(self, identity) -> str:
        """
        Process the input_data and return the processed prompt.
        
        Args:
            question_ori: The question to be processed.
        
        Returns:
            str: The processed prompt.
        """
        instruction = f"请解决以下问题：使用数字 {identity['puzzle']} 通过加减乘除得到 {identity['target']}。"
        instruction_following = """Let's think step by step and output the final answer within \\boxed{}.The final answer should be all input numbers with basic operations, and parentheses can be used to change the order of operations. For example "Final Answer: \\boxed{6+6+(6+6)}"."""
        
        prompt = instruction + '\n' + instruction_following
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _normalize_solution(solution):
        """
        Normalize the solution.
        """
        solution = solution.replace("**", "")
        solution = solution.replace("\\times", "*")
        solution = solution.replace("\\div", "/")
        solution = solution.replace("\\left", "")
        solution = solution.replace("\\right", "")
        return solution
