import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CdnaalignmentInstructionGenerator(BaseInstructionGenerator):
    """Cdnaalignment Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=100000, **kwargs):
        """
        初始化Cdnaalignment指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.n_min = n_min
        self.n_max = n_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        bases = ['A', 'C', 'G', 'T']
        s = ''.join(random.choices(bases, k=n))
        return {'n': n, 's': s}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        s = question_case['s']
        prompt = (
            "Vasya在研究生物信息学中的循环DNA序列相似性时，定义了一种新的距离度量方法——Vasya距离。给定两个长度同为n的字符串s和t，它们的Vasya距离ρ(s, t)的计算方式如下：\n\n"
            "对于每个i（0 ≤ i < n）次左循环移位后的s_i，和每个j（0 ≤ j < n）次左循环移位后的t_j，计算这两个字符串的h函数值。h函数h(s_i, t_j)统计两个字符串在相同位置上字符相同的数目。将所有i和j对应的h函数值相加，得到ρ(s, t)。\n"
            "例如，当s是'AGC'，t是'CGT'时，ρ的计算包括所有3次左移后的组合，共有3×3=9种情况。每个h函数值相加的结果为6。\n\n"
            "现在，给定一个长度为n的字符串s，要求找出所有可能的字符串t（长度同样为n），使得ρ(s, t)达到所有可能t中的最大值。由于答案可能非常大，请将结果对10^9+7取模。\n\n"
            "输入参数：\n"
            f"- 字符串长度n = {n}\n"
            f"- 字符串s = '{s}'\n\n"
            "你的任务是计算满足条件的t的数量。请将最终答案放在[answer]和[/answer]标签之间。例如，如果答案是123，则应写成[answer]123[/answer]。\n\n"
            "注意：答案必须是一个整数，且已经对10^9+7取模。"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

