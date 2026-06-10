import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import math




class BlcmInstructionGenerator(BaseInstructionGenerator):
    """Blcm Bootcamp指令生成器"""
    
    def __init__(self, min_b=1, max_b=10**6):
        """
        初始化Blcm指令生成器
        
        Args:
            min_b: 参数描述
            max_b: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数范围优化：默认上限设为1e6保证效率，同时仍覆盖所有可能情况
        确保min_b >=1 符合题目约束条件
        """
        self.min_b = max(1, min_b)  # 强制下限保护
        self.max_b = min(10**10, max_b)  # 强制上限保护
    
    def case_generator(self):
        """
        增强型case生成逻辑，确保生成案例的多样性：
        - 50%概率生成随机数
        - 30%概率生成质数
        - 20%概率生成完全平方数
        """
        choice = random.random()
        
        if choice < 0.5:
            # 生成普通随机数
            b = random.randint(self.min_b, self.max_b)
        elif choice < 0.8:
            # 生成质数（使用随机质数生成逻辑）
            primes = [x for x in self._primes_up_to(10**4) if x >= self.min_b and x <= self.max_b]
            if not primes:
                primes = [2,3,5,7,11,13,17,19,23,29]
            b = random.choice(primes)
        else:
            # 生成完全平方数（确保平方根为整数）
            sqrt_min = math.isqrt(self.min_b)
            sqrt_max = math.isqrt(self.max_b)
            sqrt_val = random.randint(sqrt_min, sqrt_max)
            b = sqrt_val * sqrt_val
        
        return {'b': b}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        b = question_case['b']
        prompt = f"""
你是一位数学专家，请解决以下问题：

给定正整数b={b}，计算当a遍历1到10^18的所有整数时，表达式[a,b]/a可能得到的不同结果的数量。其中[a,b]表示a和b的最小公倍数。

请遵循以下步骤：
1. 分析表达式[a,b]/a的数学性质
2. 推导该表达式可能值的个数与b的关系
3. 最终答案应为b的正因数个数

将答案用[answer]标签包裹，例如[answer]答案[/answer]
"""
        return prompt.strip() 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _primes_up_to(n):
        """使用Sieve算法生成质数列表"""
        sieve = [True] * (n+1)
        sieve[0:2] = [False, False]
        for i in range(2, int(math.sqrt(n)) +1):
            if sieve[i]:
                sieve[i*i : n+1 : i] = [False]*len(sieve[i*i : n+1 : i])
        return [i for i, is_prime in enumerate(sieve) if is_prime]
