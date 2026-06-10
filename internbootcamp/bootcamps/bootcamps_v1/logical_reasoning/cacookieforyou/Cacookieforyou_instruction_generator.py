import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CacookieforyouInstructionGenerator(BaseInstructionGenerator):
    """Cacookieforyou Bootcamp指令生成器"""
    
    def __init__(self, max_value=10**18):
        """
        初始化Cacookieforyou指令生成器
        
        Args:
            max_value: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_value = max_value
        self.max_retries = 1000  # 新增重试次数限制防止死循环
    
    def case_generator(self):
        rand = random.random()
        if rand < 0.25:
            return self._generate_zero_cookie_case()
        elif rand < 0.5:
            return self._generate_single_type_guest_case()
        elif rand < 0.75:
            return self._generate_yes_case()
        else:
            return self._generate_no_case()
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a = question_case['a']
        b = question_case['b']
        n = question_case['n']
        m = question_case['m']
        problem = f"""Anna has {a} vanilla and {b} chocolate cookies. She invited:
- {n} Type 1 guests (choose majority type)
- {m} Type 2 guests (choose minority type)

Determine if any guest order exists where none leave angry. 

Rules:
1. Guests arrive in any order
2. Each chooses based on current cookie counts
3. Leaves if chosen type unavailable

Answer format: [answer]Yes[/answer] or [answer]No[/answer]"""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_zero_cookie_case(self):
        """确保至少有一个客人存在"""
        a, b = 0, 0
        while True:
            n = random.randint(0, self.max_value)
            m = random.randint(0, self.max_value)
            if n + m > 0:
                return {'a': a, 'b': b, 'n': n, 'm': m}

    def _generate_single_type_guest_case(self):
        """确保至少有一类客人存在"""
        while True:
            if random.random() < 0.5:
                case = {
                    'a': random.randint(0, self.max_value),
                    'b': random.randint(0, self.max_value),
                    'n': random.randint(0, self.max_value),
                    'm': 0
                }
            else:
                case = {
                    'a': random.randint(0, self.max_value),
                    'b': random.randint(0, self.max_value),
                    'n': 0,
                    'm': random.randint(0, self.max_value)
                }
            if case['n'] + case['m'] > 0:
                return case

    def _generate_yes_case(self):
        """添加重试机制防止死循环"""
        for _ in range(self.max_retries):
            a = random.randint(0, self.max_value)
            b = random.randint(0, self.max_value)
            if a + b == 0:
                continue

            a_new, b_new = max(a, b), min(a, b)
            max_m = b_new
            m = random.randint(0, max_m)
            remaining = (a_new + b_new) - m
            n = random.randint(0, remaining)

            if n + m > 0:
                return {'a': a, 'b': b, 'n': n, 'm': m}
        # 保底生成合法案例
        return {'a': 2, 'b': 1, 'n': 1, 'm': 1}

    def _generate_no_case(self):
        strategies = [
            self._generate_case_total_exceed,
            self._generate_case_m_exceed,
            self._generate_zero_cookie_angry_case
        ]
        return random.choice(strategies)()

    def _generate_case_total_exceed(self):
        for _ in range(self.max_retries):
            a = random.randint(1, self.max_value)
            b = random.randint(1, self.max_value)
            total = a + b
            min_guest = total + 1
            n = random.randint(0, min_guest)
            m = min_guest - n
            if m < 0:
                m = 0
                n = min_guest
            if a + b < n + m:
                return {'a': a, 'b': b, 'n': n, 'm': m}
        return {'a': 1, 'b': 1, 'n': 2, 'm': 1}

    def _generate_case_m_exceed(self):
        for _ in range(self.max_retries):
            a = random.randint(0, self.max_value)
            b = random.randint(0, self.max_value)
            a_new, b_new = max(a, b), min(a, b)
            if b_new == 0:
                continue
            m = random.randint(b_new + 1, self.max_value)
            remaining = (a_new + b_new) - m
            n = random.randint(0, max(remaining, 0))
            if (n + m) <= (a_new + b_new):
                return {'a': a, 'b': b, 'n': n, 'm': m}
        return {'a': 3, 'b': 1, 'n': 1, 'm': 3}

    def _generate_zero_cookie_angry_case(self):
        return {'a': 0, 'b': 0, 
                'n': random.randint(1, self.max_value),
                'm': random.randint(0, self.max_value)}
