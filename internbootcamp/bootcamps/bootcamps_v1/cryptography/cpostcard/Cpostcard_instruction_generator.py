import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CpostcardInstructionGenerator(BaseInstructionGenerator):
    """Cpostcard Bootcamp指令生成器"""
    
    def __init__(self, max_length=200, symbol_prob=0.4):
        """
        初始化Cpostcard指令生成器
        
        Args:
            max_length: 参数描述
            symbol_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_length = max_length
        self.symbol_prob = symbol_prob
    
    def case_generator(self):
        # 生成符合字符后接符号规则的加密字符串
        encrypted = []
        length = random.randint(1, self.max_length)
        
        # 首字符必须是字母
        encrypted.append(random.choice('abcdefghijklmnopqrstuvwxyz'))
        for _ in range(1, length):
            # 前一个字符是字母时才可添加符号
            if encrypted[-1] not in ['?', '*'] and random.random() < self.symbol_prob:
                encrypted.append(random.choice(['?', '*']))
                if len(encrypted) >= length:
                    break  # 长度控制
            encrypted.append(random.choice('abcdefghijklmnopqrstuvwxyz'))
        
        encrypted_str = ''.join(encrypted[:length])
        
        # 动态计算k的范围
        min_k = self._calculate_min_length(encrypted_str)
        max_k = self._calculate_max_length(encrypted_str)
        
        # 生成k值：40%概率有效，60%概率可能越界
        if random.random() < 0.4 and max_k >= min_k:
            k = random.randint(min_k, max_k)
        else:
            k = random.randint(1, 200)
        
        return {
            'encrypted_str': encrypted_str,
            'k': k
        }
    
    @staticmethod
    def prompt_func(question_case):
        encrypted_str = question_case['encrypted_str']
        k = question_case['k']
        prompt = f'''The encrypted string rules:
1. Letters followed by '?' can be removed or kept
2. Letters followed by '*' can be removed, kept, or repeated multiple times

Given string: {encrypted_str}
Target length: {k}

Provide a valid {k}-length message or "Impossible". Place your answer within [answer][/answer].'''
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _calculate_min_length(cls, s):
        """计算最小可能长度"""
        return len(s) - 2*(s.count('?') + s.count('*'))

    @classmethod
    def _calculate_max_length(cls, s):
        """计算最大可能长度"""
        base = len(s) - s.count('?') - s.count('*')
        stars = s.count('*')
        return base + 100*stars if stars > 0 else base

    @classmethod
    def _is_case_possible(cls, s, k):
        min_len = cls._calculate_min_length(s)
        max_len = cls._calculate_max_length(s)
        return min_len <= k <= max_len

    @classmethod
    def _is_valid_solution(cls, encrypted, candidate):
        ptr = 0
        i = 0
        while i < len(encrypted):
            if i+1 < len(encrypted) and encrypted[i+1] in ['?', '*']:
                # 处理带符号的字符
                char = encrypted[i]
                symbol = encrypted[i+1]
                i += 2

                # 查找候选字符串中的匹配情况
                count = 0
                while ptr < len(candidate) and candidate[ptr] == char:
                    ptr += 1
                    count += 1

                if symbol == '?':  # 0或1次
                    if count not in [0, 1]:
                        return False
                elif symbol == '*':  # 任意次数（含0）
                    if count < 0:
                        return False
            else:
                # 处理普通字符
                if ptr >= len(candidate) or candidate[ptr] != encrypted[i]:
                    return False
                ptr += 1
                i += 1

        return ptr == len(candidate)
