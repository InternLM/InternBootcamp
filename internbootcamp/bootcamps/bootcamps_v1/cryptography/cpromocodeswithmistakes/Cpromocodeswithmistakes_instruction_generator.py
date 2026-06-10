import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from itertools import combinations




class CpromocodeswithmistakesInstructionGenerator(BaseInstructionGenerator):
    """Cpromocodeswithmistakes Bootcamp指令生成器"""
    
    def __init__(self, n=None, min_n=1, max_n=1000):
        """
        初始化Cpromocodeswithmistakes指令生成器
        
        Args:
            n: 参数描述
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n if n is not None else random.randint(min_n, max_n)
        if not (1 <= self.n <= 1000):
            raise ValueError("n must be between 1 and 1000")
    
    def case_generator(self):
        """优化后的高效生成算法"""
        n = self.n  # 使用实例的n值
        codes = set()
        full_range = list(range(10**6))
        random.shuffle(full_range)
        for num in full_range[:n]:
            codes.add(f"{num:06d}")
        return {
            'n': n,
            'promocodes': sorted(list(codes))  # 保证有序
        }
    
    @staticmethod
    def prompt_func(question_case):
        """修复后的提示生成方法"""
        n = question_case['n']  # 正确获取n值
        codes = "\n".join(question_case['promocodes'])
        return f"""计算促销码最大容错值k。规则：
1. 每个促销码为6位不同数字
2. 错误定义为任意位置数字错误
3. 找出最大k使得输入错误≤k时可唯一确定正确码

当前{n}个促销码：
{codes}

答案格式：[answer]数字[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

