import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from math import gcd
from functools import reduce
from collections import defaultdict




class CcuttingrectangleInstructionGenerator(BaseInstructionGenerator):
    """Ccuttingrectangle Bootcamp指令生成器"""
    
    def __init__(self, max_row_types=3, max_col_types=3, invalid_case_ratio=0.3):
        """
        初始化Ccuttingrectangle指令生成器
        
        Args:
            max_row_types: 参数描述
            max_col_types: 参数描述
            invalid_case_ratio: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_row_types = max_row_types
        self.max_col_types = max_col_types
        self.invalid_case_ratio = invalid_case_ratio
    
    def case_generator(self):
        # Generate valid base parameters
        is_valid = random.random() > self.invalid_case_ratio
        
        # Generate row parameters with GCD
        m = random.randint(1, self.max_row_types)
        row_gcd = random.randint(1, 5)
        row_factors = [random.randint(1, 3) for _ in range(m)]
        row_base = [row_gcd * f for f in row_factors]
        
        # Generate column parameters with GCD
        n = random.randint(1, self.max_col_types)
        col_gcd = random.randint(1, 5) if is_valid else random.randint(2, 6)
        col_factors = self._generate_coprimes(n)  # coprime factors
        col_base = [col_gcd * f for f in col_factors]
        
        # Build rectangles data
        rectangles = []
        for w in row_base:
            for h in col_base:
                rectangles.append({
                    'w': w,
                    'h': h,
                    'c': (sum(row_factors) * sum(col_factors))  # Valid baseline
                })
        
        # Introduce errors for invalid cases
        if not is_valid:
            # Corrupt either row or column base
            if random.choice([True, False]):
                row_base[0] += 1  # Break row consistency
            else:
                col_base[0] += 1  # Break column consistency
        
        # Shuffle and format output
        random.shuffle(rectangles)
        total_gcd = row_gcd * col_gcd if is_valid else 0
        
        return {
            'n': len(rectangles),
            'rectangles': [dict(r) for r in rectangles],  # Ensure serialization
            'correct_answer': self._count_ordered_factor_pairs(total_gcd) if is_valid else 0
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        rects = question_case['rectangles']
        example = "\n".join([f"{r['w']} {r['h']} {r['c']}" for r in rects])
        return f"""Calculate valid (A,B) pairs for rectangle cutting. Enclose your answer in [answer] tags.

Input:
{n}
{example}

[answer]...[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_coprimes(self, size):
        """Generate list of coprimes with guaranteed success"""
        coprimes = []
        candidates = list(range(1, 10))
        random.shuffle(candidates)

        for _ in range(size):
            for num in candidates:
                if all(gcd(num, e) == 1 for e in coprimes):
                    coprimes.append(num)
                    break
        return coprimes

    def _count_ordered_factor_pairs(self, num):
        """Accurate ordered pair counter matching problem requirements"""
        if num == 0:
            return 0

        pairs = set()
        for i in range(1, int(num**0.5)+1):
            if num % i == 0:
                pairs.add((i, num//i))
                pairs.add((num//i, i))
        return len(pairs)
