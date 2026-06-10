import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class Korpuzzle24pointsInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzle24points Bootcamp指令生成器"""
    
    def __init__(self, min_num=1, max_num=13, allow_repeats=True):
        """
        初始化Korpuzzle24points指令生成器
        
        Args:
            min_num: 参数描述
            max_num: 参数描述
            allow_repeats: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        # 参数有效性校验
        if not allow_repeats and (max_num - min_num + 1) < 4:
            raise ValueError("When allow_repeats=False, min_num and max_num must span at least 4 numbers")

        self.min_num = min_num
        self.max_num = max_num
        self.allow_repeats = allow_repeats
    
    def case_generator(self):
        MAX_ATTEMPTS = 1000
        for _ in range(MAX_ATTEMPTS):
            # 根据参数生成不同特性的数字组合
            if self.allow_repeats:
                numbers = [random.randint(self.min_num, self.max_num) for _ in range(4)]
            else:
                numbers = random.sample(range(self.min_num, self.max_num+1), 4)
            
            if self._has_solution(numbers):
                return {'numbers': sorted(numbers)}  # 排序便于后续验证
            
        raise RuntimeError("Failed to generate valid case after maximum attempts")
    
    @staticmethod
    def prompt_func(question_case) -> str:
        nums = question_case['numbers']
        example = "9 5 2 7 -> (9 - 5) × (7 - 2)" if 9 in nums else "8 2 8 2 -> 8 × (2 + 2) - 8"
        return f"""
You are a 24-point puzzle solver. Using these numbers exactly once: {', '.join(map(str, nums))},
combine them with +, -, ×, ÷ and parentheses to make 24.

Rules:
1. Use each number exactly once
2. Standard order of operations applies
3. Final result must be exactly 24

Examples:
{example}

Put your final expression within double square brackets. Example: [[(a × b) + (c ÷ d)]]
""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _has_solution(cls, numbers):
        def dfs(nums):
            if len(nums) == 1:
                return abs(nums[0] - 24) < 1e-6
            for i, a in enumerate(nums):
                for j, b in enumerate(nums):
                    if i == j:
                        continue
                    remaining = [n for idx, n in enumerate(nums) if idx not in (i,j)]
                    for op in ['+', '-', '*', '/']:
                        if op == '/' and b == 0:
                            continue
                        try:
                            res = eval(f"{a}{op}{b}") 
                            if dfs(remaining + [res]):
                                return True
                        except ZeroDivisionError:
                            continue
            return False

        return dfs(numbers)
