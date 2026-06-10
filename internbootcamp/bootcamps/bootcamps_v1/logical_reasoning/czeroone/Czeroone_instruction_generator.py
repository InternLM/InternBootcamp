import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CzerooneInstructionGenerator(BaseInstructionGenerator):
    """Czeroone Bootcamp指令生成器"""
    
    def __init__(self, **kwargs):
        """
        初始化Czeroone指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.min_length = kwargs.get('min_length', 2)
        self.max_length = kwargs.get('max_length', 10)
        self.prob_0 = kwargs.get('prob_0', 0.3)
        self.prob_1 = kwargs.get('prob_1', 0.3)
        self.prob_q = kwargs.get('prob_q', 0.4)
    
    def case_generator(self):
        length = random.randint(self.min_length, self.max_length)
        chars = []
        total = self.prob_0 + self.prob_1 + self.prob_q
        for _ in range(length):
            if total == 0:
                r = random.random() * 3
                idx = int(r % 3)
                chars.append(['0', '1', '?'][idx])
            else:
                r = random.uniform(0, total)
                if r < self.prob_0:
                    chars.append('0')
                elif r < self.prob_0 + self.prob_1:
                    chars.append('1')
                else:
                    chars.append('?')
        return {'input': ''.join(chars)}
    
    @staticmethod
    def prompt_func(question_case):
        input_str = question_case['input']
        return f"""你是解谜专家，需要解决一个名为“Zero-One”游戏的谜题。游戏规则如下：

两位玩家Masha和Petya轮流在初始的卡片序列中移除卡片。Masha先手。卡片排成一行，每次移除一张后剩余卡片左移补齐。游戏结束时剩下两张卡片组成二进制数（左侧为高位），Masha希望数值最小化，Petya希望最大化。

当前卡片序列包含模糊卡片(?可替换为0或1)，请计算所有可能的初始数值组合下游戏结束时的最终结果集合。

输入序列：{input_str}

请按字典序输出所有可能结果，每行一个，并包裹在[answer]和[/answer]标签之间，例如：
[answer]
00
01
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def compute_valid_outcomes(cls, input_str):  # 修正缩进
        n0, n1, L = 0, 0, len(input_str)
        for c in input_str:
            n0 += (c == '0')
            n1 += (c == '1')
        x = L - n0 - n1
        outcomes = set()

        if n1 <= (L-1) // 2:
            outcomes.add('00')

        L_half = L // 2
        if n0 <= L_half and L_half <= (n0 + x):
            last_char = input_str[-1] if L > 0 else ''
            if last_char == '1' or (last_char == '?' and (n1 + 1) <= (L + 1) // 2):
                outcomes.add('01')
            if last_char == '0' or (last_char == '?' and (n0 + 1) <= L_half):
                outcomes.add('10')

        if n0 <= (L-2) // 2:
            outcomes.add('11')

        return sorted(outcomes)
