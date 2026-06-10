import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from math import isqrt




class CdoublehappinessInstructionGenerator(BaseInstructionGenerator):
    """Cdoublehappiness Bootcamp指令生成器"""
    
    def __init__(self, max_r=10**5):
        """
        初始化Cdoublehappiness指令生成器
        
        Args:
            max_r: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，默认最大右边界为1e5以保证生成效率
        :param max_r: 生成区间右端点最大值，默认为100000
        """
        self.max_r = max_r
    
    def case_generator(self):
        """生成随机区间案例并准确计算答案"""
        while True:
            # 生成有效区间
            l = random.randint(1, self.max_r - 1)
            r = random.randint(l, self.max_r)
            
            # 获取区间质数
            primes = self._sieve(l, r)
            
            # 计算有效质数数量
            valid_primes = [p for p in primes if p == 2 or p % 4 == 1]
            
            # 确保生成有效案例（可包含0个解）
            return {
                'l': l,
                'r': r,
                'answer': len(valid_primes)
            }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        l = question_case['l']
        r = question_case['r']
        return f"""你是数学课代表，需要帮助Peter和Bob计算在区间[{l}, {r}]内同时满足两个条件的数字：
1. Peter条件：必须是质数（只能被1和自身整除）
2. Bob条件：可以表示为两个正整数的平方和（即存在a,b>0使得t=a²+b²）

重要数学规则：
- 根据费马定理，质数p可表示为两个平方数之和当且仅当p=2或p≡1(mod4)

请逐步分析后输出准确答案，并将最终答案放在[answer]和[/answer]标签之间。

例如：
当输入为6 66时，正确质数是13,17,29,37,41,53,61，因此输出为7

当前需要解决的输入：
l = {l}, r = {r}

请按照以下格式输出：
[answer]答案数字[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _sieve(self, l, r):
        """高效生成区间[l, r]内的质数列表"""
        if r < 2:
            return []

        # 生成基础质数用于筛法
        limit = isqrt(r) + 1
        sieve = [True] * (limit + 1)
        sieve[0:2] = [False, False]
        for i in range(2, isqrt(limit) + 1):
            if sieve[i]:
                sieve[i*i : limit+1 : i] = [False] * len(sieve[i*i : limit+1 : i])
        base_primes = [i for i, prime in enumerate(sieve) if prime]

        # 区间筛法
        segment_size = r - l + 1
        sieve = [True] * segment_size
        for p in base_primes:
            start = max(p * p, ((l + p - 1) // p) * p)
            for i in range(start, r+1, p):
                sieve[i - l] = False

        # 处理小质数的平方
        for i in range(max(2, l), isqrt(r) + 1):
            if sieve[i - l]:
                for j in range(i*i, r+1, i):
                    sieve[j - l] = False

        return [i + l for i in range(segment_size) if sieve[i]]
