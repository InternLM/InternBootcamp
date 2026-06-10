import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CnezzarandsymmetricarrayInstructionGenerator(BaseInstructionGenerator):
    """Cnezzarandsymmetricarray Bootcamp指令生成器"""
    
    def __init__(self, case_type='mixed', min_n=1, max_n=10, value_range=(1, 10000)):
        """
        初始化Cnezzarandsymmetricarray指令生成器
        
        Args:
            case_type: 参数描述
            min_n: 参数描述
            max_n: 参数描述
            value_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.case_type = case_type
        self.min_n = min_n
        self.max_n = max_n
        self.value_range = value_range
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        if self.case_type == 'valid':
            return self._generate_valid_case(n)
        elif self.case_type == 'invalid':
            return self._generate_robust_invalid_case(n)
        else:
            return random.choice([self._generate_valid_case(n), self._generate_robust_invalid_case(n)])
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        d = question_case['d']
        return f"""Determine if a symmetric array exists given the parameters:
- n = {n}
- d = {d}

A symmetric array requires:
1. Exactly 2n distinct integers
2. For each element a, there exists -a
3. Each d_i = sum of absolute differences from a_i to all elements

Output YES or NO within [answer] tags:

[answer]
{{ANSWER}}
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_case(self, n):
        min_val, max_val = self.value_range
        positives = []
        while len(positives) < n:
            num = random.randint(min_val, max_val)
            if num not in positives:
                positives.append(num)

        symmetric_array = []
        for num in positives:
            symmetric_array.extend([num, -num])
        random.shuffle(symmetric_array)

        d_array = [sum(abs(num - other) for other in symmetric_array) for num in symmetric_array]
        return {'n': n, 'd': d_array}

    def _generate_robust_invalid_case(self, n, max_attempts=10):
        # 策略1：破坏有效案例的约束条件
        for _ in range(max_attempts):
            valid_case = self._generate_valid_case(n)
            d = valid_case['d'].copy()
            sorted_d = sorted(d)

            # 破坏方法1：打破配对约束
            last_pair_index = 2*n - 2
            if sorted_d[last_pair_index] == sorted_d[last_pair_index + 1]:
                sorted_d[-1] += 1
                shuffled = sorted_d.copy()
                random.shuffle(shuffled)
                if self.check_case(n, shuffled) == 'NO':
                    return {'n': n, 'd': shuffled}

            # 破坏方法2：修改数值导致余数错误
            target_index = random.choice(range(0, 2*n, 2))
            sorted_d[target_index] += 2*n
            shuffled = sorted_d.copy()
            random.shuffle(shuffled)
            if self.check_case(n, shuffled) == 'NO':
                return {'n': n, 'd': shuffled}

        # 策略2：完全随机生成直至找到无效案例
        for _ in range(max_attempts):
            random_d = [random.randint(0, 10**6) for _ in range(2*n)]
            if self.check_case(n, random_d) == 'NO':
                return {'n': n, 'd': random_d}

        # 保底策略：构造必定失败的案例
        return {'n': n, 'd': [0]*(2*n)}

    @staticmethod
    def check_case(n, d_list):
        sorted_d = sorted(d_list)
        su = 0
        current_n = n
        valid = True

        if len(sorted_d) != 2*current_n:
            return 'NO'

        while current_n > 0 and valid:
            i = 2*current_n - 1
            if i < 1 or sorted_d[i] != sorted_d[i-1]:
                valid = False
                break

            if i > 1 and sorted_d[i] == sorted_d[i-2]:
                valid = False
                break

            total = sorted_d[i] - 2*su
            if total % (2*current_n) != 0:
                valid = False
                break

            cur = total // (2*current_n)
            if cur <= 0:
                valid = False
                break

            su += cur
            current_n -= 1

        return 'YES' if valid and current_n == 0 else 'NO'
