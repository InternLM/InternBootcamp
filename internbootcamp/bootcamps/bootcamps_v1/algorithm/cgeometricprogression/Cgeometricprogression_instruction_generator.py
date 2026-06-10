import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import defaultdict

# === 源文件中的全局函数 ===

def geometric(k, lst):
    d = defaultdict(int)
    total = 0
    for num in lst:
        if k != 0 and num % k == 0:
            total += d.get((num // k, 2), 0)
            d[(num, 2)] += d.get((num // k, 1), 0)
        d[(num, 1)] += 1
    return total


class CgeometricprogressionInstructionGenerator(BaseInstructionGenerator):
    """Cgeometricprogression Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=12, min_k=1, max_k=4, a_min=-8, a_max=8):
        """
        初始化Cgeometricprogression指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_k: 参数描述
            max_k: 参数描述
            a_min: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_k = min_k
        self.max_k = max_k
        self.a_min = a_min
        self.a_max = a_max
    
    def case_generator(self):
        k = random.randint(self.min_k, self.max_k)
        x = random.choice([num for num in range(self.a_min, self.a_max + 1) if num != 0])
        m1 = random.randint(1, 3)
        m2 = random.randint(1, 3)
        m3 = random.randint(1, 3)
        a = [x] * m1 + [x * k] * m2 + [x * k * k] * m3
        
        # Add non-interfering noise elements
        noise_count = random.randint(0, 2)
        for _ in range(noise_count):
            while True:
                noise = random.randint(self.a_min * 3, self.a_max * 3)
                if noise not in {x, x * k, x * k * k}:
                    a.append(noise)
                    break
        
        random.shuffle(a)  # 打乱顺序不影响正确性，验证时会动态计算
        
        return {
            'n': len(a),
            'k': k,
            'a': a
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        a = question_case['a']
        problem_desc = (
            "Polycarp loves geometric progressions of length three. Help him find how many such subsequences exist in his sequence with a common ratio of k.\n\n"
            "Rules:\n"
            "1. Indices must be strictly increasing (i < j < k).\n"
            "2. Elements must form a geometric progression: a[j] = a[i] * k and a[k] = a[j] * k.\n\n"
            "Input Parameters:\n"
            f"- n (array length) = {n}\n"
            f"- k (common ratio) = {k}\n"
            f"- Sequence: {a}\n\n"
            "Output the exact number of valid subsequences. Enclose your answer within [answer] and [/answer] tags."
        )
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

