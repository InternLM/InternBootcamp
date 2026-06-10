import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import math
import re




class DkuroandgcdandxorandsumInstructionGenerator(BaseInstructionGenerator):
    """Dkuroandgcdandxorandsum Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dkuroandgcdandxorandsum指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化谜题训练场类，设置生成谜题实例的参数。
        """
        self.max_a_size = params.get('max_a_size', 10)
        self.max_u = params.get('max_u', 10**5)
        self.max_x = params.get('max_x', 10**5)
        self.max_k = params.get('max_k', 10**5)
        self.max_s = params.get('max_s', 10**5)
        self.divisors = self._precompute_divisors()
    
    def case_generator(self):
        """
        生成一个包含数组a和查询条件的谜题实例。
        """
        a = []
        num_elements = random.randint(1, self.max_a_size)
        for _ in range(num_elements):
            u = random.randint(1, self.max_u)
            a.append(u)
        
        if not a:
            u = random.randint(1, self.max_u)
            a.append(u)
        
        # 随机选择一个查询条件
        x = random.randint(1, self.max_x)
        v_candidates = []
        for num in a:
            if (x + num) > self.max_s:
                continue
            if (math.gcd(x, num) % 1) != 0:  # k must divide gcd(x, v)
                continue
            v_candidates.append(num)
        
        if v_candidates:
            v = random.choice(v_candidates)
        else:
            v = -1
        
        # 生成查询条件
        k = random.choice(self.divisors[math.gcd(x, v)]) if v != -1 else 1
        s = x + v if v != -1 else random.randint(1, self.max_s)
        
        query = {
            'x': x,
            'k': k,
            's': s
        }
        
        # 确定正确答案
        correct_v = -1
        max_xor = -1
        for num in a:
            if (x + num) > s:
                continue
            if (math.gcd(x, num) % k) != 0:
                continue
            current_xor = x ^ num
            if current_xor > max_xor:
                max_xor = current_xor
                correct_v = num
        
        identity = {
            'a': a,
            'query': query,
            'correct_v': correct_v
        }
        
        return identity
    
    @staticmethod
    def prompt_func(question_case):
        """
        将谜题实例转换为问题文本。
        """
        a = question_case['a']
        query = question_case['query']
        x = query['x']
        k = query['k']
        s = query['s']
        
        prompt = (
            f"数组a的元素是 {a}。现在，给定x={x}，k={k}，s={s}。请找出数组中满足以下条件的v：\n"
            "1. k必须能整除x和v的最大公约数。\n"
            "2. x + v ≤ s。\n"
            "3. x XOR v的值最大。\n"
            "如果没有满足条件的v，返回-1。\n"
            "请将答案放在[answer]标签内，例如：\n"
            "[answer]123[/answer]\n"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _precompute_divisors(self):
        max_num = self.max_u
        divisors = [[] for _ in range(max_num + 1)]
        for i in range(1, max_num + 1):
            for j in range(i, max_num + 1, i):
                divisors[j].append(i)
        return divisors
