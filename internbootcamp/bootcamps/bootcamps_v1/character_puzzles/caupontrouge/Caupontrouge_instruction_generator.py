import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
from itertools import combinations




class CaupontrougeInstructionGenerator(BaseInstructionGenerator):
    """Caupontrouge Bootcamp指令生成器"""
    
    def __init__(self, max_length=10, max_m=5):
        """
        初始化Caupontrouge指令生成器
        
        Args:
            max_length: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        优化参数校验和字符多样性保证:
        1. 限制max_length >=3保证有效分割
        2. 强制字符串至少包含两个不同字符
        """
        self.max_length = max(max_length, 3)
        self.max_m = max_m
    
    def case_generator(self):
        """增强案例生成鲁棒性"""
        import random
        from random import randint
        
        while True:
            # 生成符合要求的字符串
            n = randint(3, self.max_length)
            m = randint(1, min(n-1, self.max_m))
            
            # 生成包含至少两个不同字符的字符串
            while True:
                s = ''.join([chr(randint(97, 99)) for _ in range(n)])
                if len(set(s)) >= 2: break
            
            # 获取有效候选集
            candidates = self._get_all_candidates(s, m)
            if len(candidates) >= max(3, m):  # 保证足够测试意义
                k = randint(1, len(candidates))
                return {
                    'n': n, 'm': m, 'k': k, 's': s,
                    'candidates': sorted(candidates, reverse=True)
                }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""给定字符串{question_case['s']!r}，请分割为{question_case['m']}个非空子串。
所有可能分割方案中的最小标签按逆字典序排列后，求第{question_case['k']}个标签。
答案请用[answer]标签包裹，如：[answer]答案[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _get_all_candidates(self, s, m):
        """优化分割点生成算法"""
        candidates = set()
        n = len(s)

        # 使用迭代器避免内存爆炸
        for splits in combinations(range(1, n), m-1):
            parts = []
            prev = 0
            for pos in sorted(splits):
                parts.append(s[prev:pos])
                prev = pos
            parts.append(s[prev:])
            candidates.add(min(parts))

        return sorted(candidates)
