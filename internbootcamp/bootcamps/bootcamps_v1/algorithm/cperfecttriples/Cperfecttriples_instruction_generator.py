import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CperfecttriplesInstructionGenerator(BaseInstructionGenerator):
    """Cperfecttriples Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10**6):
        """
        初始化Cperfecttriples指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        # 生成策略：25%小值，25%中等值，50%参数范围
        rand = random.random()
        if rand < 0.25:
            n = random.randint(1, 10)        # 基础测试样例区
        elif rand < 0.5:
            n = random.randint(100, 10**4)   # 中等规模测试区
        else:
            n = random.randint(self.min_n, self.max_n)
        return {'n': n}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        return f"""Given n = {n}, compute the n-th element in the XOR triple sequence. Rules:
1. Sequence is built by adding lex smallest (a,b,c) with a^b^c=0
2. Each triple's elements are appended in order
3. Sequence starts with 1,2,3,4,8,12,5,10,15...

Put your final answer within [answer] tags like: [answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _get_st2(cls, count):
        """ 优化st2计算：通过位长度快速定位起始点 """
        if count == 0:
            return 0
        target = 3 * count
        bit_len = target.bit_length()
        exponent = (bit_len + 1) // 2  # 4^exponent初始估算
        st2 = 1 << (2 * exponent)

        # 精确调整
        while st2 > target:
            exponent -= 1
            st2 >>= 2
        while st2 * 4 <= target:
            st2 <<= 2
        return st2

    @classmethod
    def _getFirstInTriple(cls, count):
        st2 = cls._get_st2(count)
        return st2 + count - (st2 - 1) // 3 - 1

    @classmethod
    def _getValue(cls, position):
        # 保持原算法结构，优化计算效率
        triple_index = (position + 2) // 3
        first = cls._getFirstInTriple(triple_index)

        mod = position % 3
        if mod == 1:
            return first

        # 公共计算逻辑提取
        res = 0
        value = 1
        f = first
        while f > 0:
            x = f & 3
            if mod == 2:
                res += (value << 1) if x == 1 else (3*value if x ==2 else value)
            else:
                res += (3*value) if x ==1 else (value<<1 if x==3 else value)
            value <<= 2
            f >>= 2
        return res
