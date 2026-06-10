import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class ClunarnewyearandnumberdivisionInstructionGenerator(BaseInstructionGenerator):
    """Clunarnewyearandnumberdivision Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=8, max_num=10000):
        """
        初始化Clunarnewyearandnumberdivision指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_num: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """参数初始化增强校验"""
        # 确保min_n是偶数且≥2
        self.min_n = max(2, min_n)
        if self.min_n % 2 != 0:
            self.min_n += 1

        # 确保max_n是偶数且≥min_n
        self.max_n = max(self.min_n, max_n)
        if self.max_n % 2 != 0:
            self.max_n -= 1
            if self.max_n < self.min_n:
                self.max_n = self.min_n
        self.max_num = max_num
    
    def case_generator(self):
        """完全随机案例生成"""
        possible_n = list(range(self.min_n, self.max_n+1, 2))
        n = random.choice(possible_n)
        numbers = [random.randint(1, self.max_num) for _ in range(n)]
        
        # 严格遵循最优解生成逻辑
        sorted_nums = sorted(numbers)
        sum_sq = 0
        lo, hi = 0, n-1
        while lo < hi:
            sum_sq += (sorted_nums[lo] + sorted_nums[hi])**2
            lo += 1
            hi -= 1
            
        return {
            'n': n,
            'numbers': numbers,
            'correct': sum_sq
        }
    
    @staticmethod
    def prompt_func(case):
        """增强格式说明"""
        return f"""春节数学作业题：将以下{case['n']}个数字分成若干组（每组至少2个），求各组和平方的最小值。

输入：
{case['n']}
{' '.join(map(str, case['numbers']))}

要求输出格式示例：[answer]答案[/answer]，如[answer]164[/answer]

计算时请严格按照排序配对规则：先将数字排序，然后将最小和最大的配对组合。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

