import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from bisect import bisect_right as bisect
import re




class CrestoringpermutationInstructionGenerator(BaseInstructionGenerator):
    """Crestoringpermutation Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=5, unsolvable_prob=0.2):
        """
        初始化Crestoringpermutation指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            unsolvable_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.unsolvable_prob = unsolvable_prob
    
    def case_generator(self):
        if random.random() < self.unsolvable_prob:
            n = random.randint(self.min_n, self.max_n)
            case_type = random.choice([1, 2])
            b = []
            if case_type == 1:
                b = [2 * n]
                remaining = list(range(1, 2 * n))
                if n > 1:
                    others = random.sample(remaining, n-1)
                    b.extend(others)
            else:
                possible = list(range(2, 2 * n + 1))
                b = random.sample(possible, k=n)
            random.shuffle(b)
            return {
                'n': n,
                'b': b,
                'expected': -1
            }
        else:
            while True:
                n = random.randint(self.min_n, self.max_n)
                possible_values = list(range(1, 2 * n + 1))
                if 2 * n in possible_values:
                    possible_values.remove(2 * n)
                if 1 not in possible_values:
                    continue
                b = [1]
                if n > 1:
                    remaining = possible_values.copy()
                    remaining.remove(1)
                    others = random.sample(remaining, n-1)
                    b.extend(others)
                if len(set(b)) != n or 2 * n in b or 1 not in b:
                    continue
                sorted_b = sorted(b)
                l = sorted([num for num in range(1, 2 * n + 1) if num not in sorted_b])
                d = {}
                f = 0
                for bi in sorted_b:
                    pos = bisect(l, bi)
                    if pos >= len(l):
                        f = 1
                        break
                    selected = l[pos]
                    d[bi] = selected
                    del l[pos]
                if f:
                    continue
                a = []
                for num in sorted_b:
                    a.append(num)
                    a.append(d[num])
                return {
                    'n': n,
                    'b': b,
                    'expected': a
                }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        b = question_case['b']
        prompt = f"""You are given a sequence b of length {n}. Find the lexicographically smallest permutation a of 1 to {2*n} such that for each i (1 ≤ i ≤ {n}), b[i] is the minimum of a[2i-1] and a[2i]. If impossible, output -1.

Input:
n = {n}
b = {b}

Format your answer as space-separated numbers within [answer] tags. Example:
[answer]1 2 3 4[/answer] or [answer]-1[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

