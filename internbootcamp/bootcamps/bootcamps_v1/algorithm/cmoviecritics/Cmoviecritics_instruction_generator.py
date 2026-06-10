import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from random import shuffle
from random import choices




class CmoviecriticsInstructionGenerator(BaseInstructionGenerator):
    """Cmoviecritics Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cmoviecritics指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 10)
        self.k = params.get('k', 3)
        if self.k > self.n:
            self.k = self.n  # 确保k不超过n
    
    def case_generator(self):
        n = self.n
        k = self.k

        # 生成包含每个类型至少一次的电影序列
        a = list(range(1, k + 1))
        remaining = n - k
        if remaining > 0:
            a += choices(range(1, k + 1), k=remaining)
        shuffle(a)  # 打乱顺序以增加随机性

        # 计算每个类型被排除后的压力次数
        def calculate_stress(x):
            filtered = [num for num in a if num != x]
            if len(filtered) <= 1:
                return 0
            stress = 0
            for i in range(1, len(filtered)):
                if filtered[i] != filtered[i-1]:
                    stress += 1
            return stress

        min_stress = float('inf')
        best_x = None
        for x in range(1, k + 1):
            stress = calculate_stress(x)
            if stress < min_stress:
                min_stress = stress
                best_x = x
            elif stress == min_stress:
                if x < best_x:
                    best_x = x

        # 返回问题实例
        return {
            'n': n,
            'k': k,
            'a': a,
            'correct_answer': best_x
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        a = question_case['a']
        a_str = ', '.join(map(str, a))
        prompt = (
            f"电影节有{n}天，每天放一部电影。电影的类型序列是：{a_str}。\n"
            f"Valentine想排除一个类型，使得剩下的电影中的类型变化次数最少。你应该排除哪个类型？\n"
            f"请把答案放在[answer]标签中，例如[answer]3[/answer]。"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

