import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CvusthecossackandstringsInstructionGenerator(BaseInstructionGenerator):
    """Cvusthecossackandstrings Bootcamp指令生成器"""
    
    def __init__(self, a_min_len=5, a_max_len=20, **kwargs):
        """
        初始化Cvusthecossackandstrings指令生成器
        
        Args:
            a_min_len: 参数描述
            a_max_len: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.a_min_len = max(a_min_len, 1)
        self.a_max_len = max(a_max_len, self.a_min_len + 1)
    
    def case_generator(self):
        # 保证 a长度 ≥ b长度
        a_len = random.randint(self.a_min_len, self.a_max_len)
        b_len = random.randint(1, a_len)  # 确保1 ≤ |b| ≤ |a|
        
        # 生成合法二进制字符串对
        while True:
            a = ''.join(random.choices('01', k=a_len))
            b = ''.join(random.choices('01', k=b_len))
            
            # 计算正确答案
            expected = self._calculate_ground_truth(a, b)
            if expected > 0:  # 确保至少存在有效解
                return {
                    'a': a,
                    'b': b,
                    '_ground_truth': expected
                }
    
    @staticmethod
    def prompt_func(question_case):
        a = question_case['a']
        b = question_case['b']
        return f"""给定两个二进制字符串a和b，其中|b| ≤ |a|。计算a中所有长度为|b|的子串c，使得b与c的对应位差异数为偶数的子串数量。

输入：
a = {a} (长度={len(a)})
b = {b} (长度={len(b)})

请输出确切的整数答案，格式示例：[answer]5[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _calculate_ground_truth(self, a, b):
        """基于参考代码的高效实现"""
        m = len(b)
        n = len(a)
        if m > n:
            return 0

        c2 = sum(1 for c in b if c == '1') % 2
        c1 = sum(1 for c in a[:m] if c == '1')
        res = (c1 % 2) == c2

        for i in range(m, n):
            c1 += (a[i] == '1') - (a[i - m] == '1')
            res += (c1 % 2) == c2
        return res
