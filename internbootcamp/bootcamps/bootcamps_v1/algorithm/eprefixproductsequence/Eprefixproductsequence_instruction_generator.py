import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class EprefixproductsequenceInstructionGenerator(BaseInstructionGenerator):
    """Eprefixproductsequence Bootcamp指令生成器"""
    
    def __init__(self, max_n=100000, min_n=1):
        """
        初始化Eprefixproductsequence指令生成器
        
        Args:
            max_n: 参数描述
            min_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，确保n的取值范围合法。

        参数:
            max_n (int): 生成的n的最大值（默认1e5，须小于等于1e5）
            min_n (int): 生成的n的最小值（默认1，须大于等于1）
        """
        if min_n < 1:
            raise ValueError("min_n must be at least 1")
        if max_n > 10**5:
            raise ValueError("max_n cannot exceed 100000")
        if min_n > max_n:
            raise ValueError("min_n must be <= max_n")
        self.max_n = max_n
        self.min_n = min_n
    
    def case_generator(self):
        """
        生成n时确保覆盖所有边界条件：
        - 强制包含n=1,4以确保特殊案例覆盖率
        - 50%概率生成质数用于覆盖YES案例
        """
        candidates = []
        if self.min_n <= 1 <= self.max_n:
            candidates.append(1)
        if self.min_n <= 4 <= self.max_n:
            candidates.append(4)
        # 随机生成至少一个质数案例（若范围内存在）
        prime_candidate = self._find_prime_in_range()
        if prime_candidate:
            candidates.append(prime_candidate)
        
        # 随机选择n（优先特殊案例）
        if candidates and random.random() < 0.5:
            n = random.choice(candidates)
        else:
            n = random.randint(self.min_n, self.max_n)
        
        possible = n in (1, 4) or self.is_prime(n)
        return {'n': n, 'possible': possible}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """优化问题描述的数学表达式清晰度"""
        n = question_case['n']
        problem_desc = (
            f"给定整数 n = {n}，寻找一个排列 P = [a₁, a₂, ..., aₙ] 满足：\n\n"
            "条件定义：\n"
            f"- 前缀积序列 B = [b₁, b₂, ..., bₙ]，其中 b_i = (a₁×a₂×...×a_i) mod {n}\n"
            f"- 要求 B 是 [0, 1, 2, ..., {n-1}] 的一个排列\n\n"
            "输出要求：\n"
            f"1. 第一行输出是否存在解（YES/NO）\n"
            f"2. 若存在解，输出{n}行具体排列（每行一个整数）\n\n"
            "答案格式要求：\n"
            "将完整输出包含在[answer]和[/answer]标记之间，例如：\n"
            "[answer]\n"
            "YES\n1\n3\n2\n4\n[/answer]"
        )
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def is_prime(n):
        """优化质数判断逻辑，提升大数效率"""
        if n < 2:
            return False
        if n % 2 == 0:
            return n == 2
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True

    def _find_prime_in_range(self):
        """在允许范围内查找一个质数"""
        attempts = 0
        while attempts < 1000:
            n = random.randint(self.min_n, self.max_n)
            if self.is_prime(n):
                return n
            attempts += 1
        return None  # 未找到时不强制要求
