import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class BplusandmultiplyInstructionGenerator(BaseInstructionGenerator):
    """Bplusandmultiply Bootcamp指令生成器"""
    
    def __init__(self, a_min=1, a_max=100, b_min=1, b_max=100, n_min=1, n_max=10**9, seed=None):
        """
        初始化Bplusandmultiply指令生成器
        
        Args:
            a_min: 参数描述
            a_max: 参数描述
            b_min: 参数描述
            b_max: 参数描述
            n_min: 参数描述
            n_max: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.a_min = a_min
        self.a_max = a_max
        self.b_min = b_min
        self.b_max = b_max
        self.n_min = n_min
        self.n_max = n_max
        self.rng = random.Random(seed)
    
    def case_generator(self):
        # 强制生成20% a=1的案例以覆盖特殊情况
        if self.rng.random() < 0.2:
            a = 1
        else:
            a = self.rng.randint(self.a_min, self.a_max)
        
        b = self.rng.randint(self.b_min, self.b_max)
        
        # 当a=1时，确保生成有效的正例和反例
        if a == 1:
            if self.rng.random() < 0.5:
                # 生成有效n=1 + k*b
                k = self.rng.randint(0, 10)
                n = 1 + k * b
            else:
                # 生成无效n
                while True:
                    n = self.rng.randint(self.n_min, self.n_max)
                    if (n - 1) % b != 0:
                        break
        else:
            # 生成可能合法的普通案例
            steps = self.rng.randint(0, 5)
            now = 1
            for _ in range(steps):
                if self.rng.random() < 0.5:
                    now *= a
                else:
                    now += b
            n = self.rng.choice([
                now * a**self.rng.randint(0,3) + b*self.rng.randint(0,10),
                self.rng.randint(self.n_min, self.n_max)
            ])
        
        return {'n': n, 'a': a, 'b': b}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        b = question_case['b']
        return f"""你正在解决一个数学谜题，需要判断数字{n}是否属于特定无限集合。集合生成规则如下：
1. 初始元素为1
2. 如果x在集合中，则x*a和x+b也在集合中

请判断给定数值n={n}（a={a}, b={b}）是否属于该集合，并将答案（Yes/No）包裹在[answer]标签中，如：[answer]Yes[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def check_in_set(n, a, b):
        if n == 1:
            return True
        max_multiplier = 0
        current = 1
        while current <= n:
            if (n - current) % b == 0:
                return True
            if a == 1:
                return False  # 避免无限循环
            prev = current
            current *= a
            if current == prev:  # 防止a=1时的无限循环
                break
        return False
