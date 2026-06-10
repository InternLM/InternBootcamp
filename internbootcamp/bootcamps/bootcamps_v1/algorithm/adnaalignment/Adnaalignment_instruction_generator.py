import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class AdnaalignmentInstructionGenerator(BaseInstructionGenerator):
    """Adnaalignment Bootcamp指令生成器"""
    
    def __init__(self, n=None, min_n=1, max_n=100000, seed=None):
        """
        初始化Adnaalignment指令生成器
        
        Args:
            n: 参数描述
            min_n: 参数描述
            max_n: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        if n is not None and not (1 <= n <= 10**5):
            raise ValueError("n must be between 1 and 1e5")
        self.n = n
        self.min_n = max(1, min(min_n, 10**5))
        self.max_n = min(max_n, 10**5)
        self.rng = random.Random(seed)
    
    def case_generator(self):
        chars = ['A', 'C', 'G', 'T']
        n = self.n if self.n is not None else self.rng.randint(self.min_n, self.max_n)
        s = ''.join(self.rng.choices(chars, k=n))
        return {'n': n, 's': s}
    
    @staticmethod
    def prompt_func(question_case):
        case = question_case
        return f"""给定DNA字符串长度n={case['n']}，原始字符串s={case['s']}，计算使得Vasya距离ρ(s,t)最大的不同字符串t的数量（模{MOD}）。

Vasya距离定义：遍历s和t的所有循环移位组合，统计相同位置字符匹配的总次数。

答案请用[answer]答案[/answer]标记。例如：[answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

