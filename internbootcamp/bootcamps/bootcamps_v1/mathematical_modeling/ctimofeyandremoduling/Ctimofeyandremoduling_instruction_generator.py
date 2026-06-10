import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import random
import re




class CtimofeyandremodulingInstructionGenerator(BaseInstructionGenerator):
    """Ctimofeyandremoduling Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ctimofeyandremoduling指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.m = params.get('m', 17)
        self.n = params.get('n', 5)
    
    def case_generator(self):
        m = self.m
        n = self.n
        if m < 2:
            m = 2
        if n < 1 or n > 10**5:
            n = min(max(n, 1), 10**5)
        x = random.randint(0, m - 1)
        if n == 1:
            d = random.randint(0, m - 1)
        else:
            d = random.randint(1, m - 1)
        a = [(x + i * d) % m for i in range(n)]
        random.shuffle(a)
        return {
            "m": m,
            "n": n,
            "a": a
        }
    
    @staticmethod
    def prompt_func(question_case):
        m = question_case['m']
        n = question_case['n']
        a = question_case['a']
        a_str = ', '.join(map(str, a))
        prompt = f"Timofey有一个序列：{a_str}，模数m={m}。他想知道是否可以将这个序列重新排列成一个模{m}的算术级数。如果可以，请给出首项x和公差d；否则输出-1。答案格式：[answer]x d[/answer]。"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

