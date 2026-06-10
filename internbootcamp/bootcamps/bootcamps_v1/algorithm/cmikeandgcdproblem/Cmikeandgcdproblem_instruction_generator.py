import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from math import gcd
from functools import reduce




class CmikeandgcdproblemInstructionGenerator(BaseInstructionGenerator):
    """Cmikeandgcdproblem Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=10**5, max_value=10**9):
        """
        初始化Cmikeandgcdproblem指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            max_value: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.max_value = max_value
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        # 决定生成类型：50%概率生成可立即解决的案例，50%需要计算的案例
        if random.choice([True, False]):
            # 生成初始gcd>1的情况
            d = random.randint(2, 5)
            a = [d * random.randint(1, self.max_value//d) for _ in range(n)]
        else:
            # 生成初始gcd=1的数组（必须通过操作解决）
            while True:
                # 生成至少两个互质数确保整体gcd=1
                a = []
                # 生成前两个互质数
                x, y = random.sample(range(1, self.max_value//2 +1), 2)
                while gcd(x, y) != 1:
                    x, y = random.sample(range(1, self.max_value//2 +1), 2)
                a.extend([x, y])
                # 生成其余元素
                for _ in range(n-2):
                    a.append(random.randint(1, self.max_value))
                # 验证整体gcd
                if reduce(gcd, a) == 1:
                    break
        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        a_str = ' '.join(map(str, question_case['a']))
        return f"""给定长度为{question_case['n']}的数列: {a_str}
请你判断是否可以通过替换相邻两数为它们的差和和（操作次数最少），使得数列所有元素的最大公约数大于1。若可以，输出YES并给出最少操作数，否则输出NO。答案格式：[answer]YES\nX[/answer] 或 [answer]NO[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

