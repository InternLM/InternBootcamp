import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
import math
from collections import defaultdict




class CarpaandagamewithmojtabaInstructionGenerator(BaseInstructionGenerator):
    """Carpaandagamewithmojtaba Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Carpaandagamewithmojtaba指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'min_n': 1,
            'max_n': 100,
            'max_prime': 50,    # 最大质数范围
            'max_factors': 3,   # 每个数的最大质因子数
            'max_exponent': 5   # 每个因子的最大指数
        }
        self.params.update(params)
    
    def case_generator(self):
        n = random.randint(self.params['min_n'], self.params['max_n'])
        primes = self._generate_primes(self.params['max_prime'], self.params['max_factors'] + 1)
        a = []
        for _ in range(n):
            num = self._generate_number(primes)
            a.append(num)
        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = ' '.join(map(str, question_case['a']))
        return (
            "Mojtaba and Arpa are playing a number game. The rules are:\n"
            "1. On a turn, choose a prime power p^k that divides at least one number\n"
            "2. For each x divisible by p^k, replace x with x/(p^k)\n"
            "3. The player who cannot make a move loses\n\n"
            f"Input:\n{n}\n{a}\n\n"
            "Determine the winner (Mojtaba or Arpa). Put your final answer within [answer]...[/answer]."
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_primes(self, max_val, count):
        primes = []
        for num in range(2, max_val + 1):
            if self._is_prime(num):
                primes.append(num)
                if len(primes) >= count:
                    break
        return primes

    def _generate_number(self, available_primes):
        factors = random.sample(available_primes, random.randint(0, min(len(available_primes), self.params['max_factors'])))
        number = 1
        for p in factors:
            exponent = random.randint(1, self.params['max_exponent'])
            number *= p ** exponent
        return number if number != 1 else random.choice([1, 1, 1, 2])  # 增加1的概率但允许少量质数

    @staticmethod
    def _is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
