import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CstrangefunctionInstructionGenerator(BaseInstructionGenerator):
    """Cstrangefunction Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10**16, include_boundary=True):
        """
        初始化Cstrangefunction指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            include_boundary: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if min_n < 1:
            raise ValueError("min_n must be at least 1")
        if max_n < min_n:
            raise ValueError("max_n must be greater than or equal to min_n")
        self.min_n = min_n
        self.max_n = max_n
        self.include_boundary = include_boundary
    
    def case_generator(self):
        # 生成具有全面覆盖的测试用例
        if self.include_boundary and random.random() < 0.15:
            boundary_n = [1, 2, 3, 4, 10, 10000000000000000]
            n = random.choice(boundary_n)
        else:
            r = random.random()
            if r < 0.3:  # 30%小值
                n = random.randint(1, 100)
            elif r < 0.6:  # 30%中等值
                n = random.randint(10**3, 10**6)
            elif r < 0.85:  # 25%大值
                n = random.randint(10**9, 10**12)
            else:  # 15%极值
                n = random.randint(10**15, self.max_n)
            n = max(self.min_n, min(n, self.max_n))
        return {'n': n}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        return f"""请计算∑f(i) mod 1e9+7（1≤i≤{n}），其中f(i)是i的最小非因数。
规则说明：
1. f(i)定义为i的最小非除数正整数
2. 例如f(4)=3，因为1、2是4的因数但3不是
3. 总和需要对1e9+7取模

输出要求：
将最终答案放在[answer]标签内，如[answer]123[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_answer(n):
        # 优化后的参考实现
        FACT = [1,2,3,4,5,7,8,9,11,13,16,17,19,23,25,27,29,31,32,37,41,43]
        MOD = 10**9+7
        res = n % MOD
        idx = 0

        while idx < len(FACT):
            # 计算当前阶乘基
            product = 1
            for f in reversed(FACT[:idx+1]):
                if product % f != 0:
                    product *= f
                    if product > n:
                        break

            if product > n:
                break

            # 计算贡献值
            offset = FACT[idx+1] - FACT[idx] if idx > 0 else 1
            count = (n - product) // product + 1
            res = (res + count * offset) % MOD
            idx += 1

        return res
