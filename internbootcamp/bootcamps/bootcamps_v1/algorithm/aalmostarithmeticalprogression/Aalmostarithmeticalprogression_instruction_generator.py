import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict




class AalmostarithmeticalprogressionInstructionGenerator(BaseInstructionGenerator):
    """Aalmostarithmeticalprogression Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Aalmostarithmeticalprogression指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.max_n = min(params.get('max_n', 50), 4000)
        self.min_val = max(params.get('min_val', 1), 1)
        self.max_val = min(params.get('max_val', 10**6), 10**6)
    
    def case_generator(self):
        # 生成策略优化：覆盖边界情况及有效AAP结构
        if random.random() < 0.3:
            # 边界情况生成
            return self._generate_edge_case()
        else:
            return self._generate_standard_case()
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case["n"]
        b = " ".join(map(str, question_case["b"]))
        return f"""Find the length of the longest subsequence that forms an almost arithmetical progression (AAP) where:
- a₁ is any integer
- For i > 1: aᵢ = aᵢ₋₁ + (-1)^(i+1)·q (q is integer)

Input:
{n}
{b}

Output format: Only the integer answer within [answer] tags, like:
[answer]4[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_edge_case(self):
        """生成边界测试用例（全相同元素、交替元素等）"""
        case_type = random.choice([
            'all_same', 
            'alternating',
            'single_element'
        ])

        if case_type == 'all_same':
            n = random.randint(1, self.max_n)
            val = random.randint(self.min_val, self.max_val)
            return {
                "n": n,
                "b": [val]*n,
                "ans": n
            }

        elif case_type == 'alternating':
            n = random.randint(2, self.max_n)
            a, b = random.sample(range(self.min_val, self.max_val+1), 2)
            return {
                "n": n,
                "b": [a, b]*(n//2) + [a]*(n%2),
                "ans": n
            }

        else:  # single_element
            return {
                "n": 1,
                "b": [random.randint(self.min_val, self.max_val)],
                "ans": 1
            }

    def _generate_standard_case(self):
        """标准案例生成逻辑改进"""
        # 构造有效AAP序列
        base_len = random.randint(3, self.max_n)
        aap = self._generate_valid_aap(base_len)

        # 插入噪声元素
        noise_num = random.randint(0, self.max_n - base_len)
        b = self._insert_noise(aap, noise_num)
        random.shuffle(b)  # 保持子序列顺序但不要求连续

        return {
            "n": len(b),
            "b": b,
            "ans": self.calculate_max_aap_length(b)
        }

    def _generate_valid_aap(self, length):
        """生成符合AAP定义的基准序列"""
        p = random.randint(self.min_val, self.max_val)
        q = random.randint(1, (self.max_val - self.min_val)//2)
        sequence = [p]
        for i in range(1, length):
            sign = (-1)**(i+1)
            sequence.append(sequence[i-1] + sign * q)
        return sequence

    def _insert_noise(self, base, noise_num):
        """随机插入噪声元素"""
        for _ in range(noise_num):
            insert_pos = random.randint(0, len(base))
            base.insert(insert_pos, random.randint(self.min_val, self.max_val))
        return base

    @staticmethod
    def calculate_max_aap_length(b):
        """精确实现原题解算法"""
        n = len(b)
        if n <= 1:
            return n

        max_len = 1
        dp = defaultdict(lambda: defaultdict(int))

        for i in range(n):
            for j in range(i+1, n):
                key = (b[i], b[j] - ((-1)**(2+1)) * (b[j] - b[i]))
                dp[j][key] = max(dp[j].get(key, 0), dp[i].get(key, 1) + 1)
                max_len = max(max_len, dp[j][key])

        return max(max_len, 2 if n >=2 else 1)
