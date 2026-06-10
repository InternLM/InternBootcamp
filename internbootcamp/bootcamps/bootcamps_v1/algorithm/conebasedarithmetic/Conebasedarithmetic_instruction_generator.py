import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from functools import lru_cache




class ConebasedarithmeticInstructionGenerator(BaseInstructionGenerator):
    """Conebasedarithmetic Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10**15-1):
        """
        初始化Conebasedarithmetic指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        # 预处理生成1~17位的全1数
        self.a = [0]
        for i in range(1, 17+1):
            self.a.append(self.a[-1] * 10 + 1)
    
    def case_generator(self):
        # 生成三类测试用例：全1数、接近全1数的边缘值、随机数
        rand = random.random()
        if rand < 0.2:  # 全1数
            digits = random.randint(1, 17)
            n = self.a[digits]
        elif rand < 0.4:  # 全1数±1
            digits = random.randint(2, 16)
            base = self.a[digits]
            n = base + random.choice([-1, 1])
        else:  # 普通随机数
            n = random.randint(self.min_n, min(self.max_n, 10**17))
        return {'n': n}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        return (
            f"将整数 {n} 表示为全1数字的加减组合，找到最少需要使用的1的总个数。\n"
            "规则说明：\n"
            "1. 每个加数/减数必须是由连续1组成的整数（如11, 111等）\n"
            "2. 允许使用加减法组合，例如：121 = 111 + 11 - 1\n"
            "3. 要求最终解中使用的1字符总数最少\n\n"
            "请给出最少需要的1的总个数，并置于[answer]标签内，例如：[answer]6[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @lru_cache(maxsize=None)
    def calculate_min_ones(self, n):
        def dfs(n, p):
            if p == 0:
                return float('inf') if n !=0 else 0

            current = self.a[p]
            if current == 0:
                return dfs(n, p-1)

            quotient, remainder = divmod(n, current)

            if remainder == 0:
                return quotient * p

            # 正向处理方案
            option1 = quotient * p + dfs(remainder, p-1)
            # 溢出处理方案（多用一个current）
            option2 = (quotient + 1) * p + dfs(current*(quotient+1)-n, p-1)

            return min(option1, option2)

        return dfs(n, p=len(self.a)-1)  # 从最大位数开始处理
