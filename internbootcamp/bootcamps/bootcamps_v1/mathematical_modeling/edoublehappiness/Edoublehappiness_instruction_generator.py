import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from math import isqrt




class EdoublehappinessInstructionGenerator(BaseInstructionGenerator):
    """Edoublehappiness Bootcamp指令生成器"""
    
    def __init__(self, max_limit=100000):
        """
        初始化Edoublehappiness指令生成器
        
        Args:
            max_limit: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        Initialize bootcamp with safe parameters for case generation
        - max_limit capped at 1e6 to prevent memory overflow
        - Dynamic sieve generation for case validity
        """
        super().__init__()
        self.max_limit = min(max_limit, 1000000)  # Safety cap
    
    def case_generator(self):
        """Generate valid cases using optimized prime checking"""
        # Generate valid range with safe boundaries
        r = random.randint(2, self.max_limit)
        l = random.randint(1, r)
        
        # Count qualifying numbers using optimized method
        count = 0
        if l <= 2 <= r:
            count += 1
        
        # Check numbers congruent 1 mod4 for primality
        start = max(l, 5)
        for num in range(start, r + 1):
            if num % 4 != 1:
                continue
            if self.is_prime(num):
                count += 1
                
        return {'l': l, 'r': r, 'answer': count}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        l, r = question_case['l'], question_case['r']
        return f"""Find numbers between {l} and {r} (inclusive) that are:
1. Prime numbers
2. Expressible as sum of two squares (a² + b²)

Output format: [answer]<number>[/answer]
Example: For input 3-5, correct answer is [answer]1[/answer]

Calculate for {l}-{r}:""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def is_prime(n):
        """Optimized primality test"""
        if n <= 1:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        for i in range(5, isqrt(n)+1, 6):
            if n % i == 0 or n % (i+2) == 0:
                return False
        return True
