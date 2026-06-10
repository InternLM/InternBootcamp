import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CaliceboborangesandapplesInstructionGenerator(BaseInstructionGenerator):
    """Caliceboborangesandapples Bootcamp指令生成器"""
    
    def __init__(self, max_value=10**3, probability_impossible=0.3, seed=None):
        """
        初始化Caliceboborangesandapples指令生成器
        
        Args:
            max_value: 参数描述
            probability_impossible: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.max_value = max_value
        self.probability_impossible = probability_impossible
        self.rng = random.Random(seed)
    
    def case_generator(self):
        for _ in range(100):
            generate_impossible = self.rng.random() < self.probability_impossible
            x = self.rng.randint(1, self.max_value)
            y = self.rng.randint(1, self.max_value)
            if x * y <= 1:
                continue
            possible = self.check_solution_exists(x, y)
            if generate_impossible:
                if not possible:
                    return {'x': x, 'y': y}
            else:
                if possible:
                    return {'x': x, 'y': y}
        return {'x': 3, 'y': 2}
    
    @staticmethod
    def prompt_func(question_case):
        x = question_case['x']
        y = question_case['y']
        prompt = f"""Alice and Bob discovered {x} oranges and {y} apples. They each took one fruit and created a card game to distribute the rest. 

Rules:
- Card 'A': Alice gives all her fruits to Bob and replaces them from the bag
- Card 'B': Bob gives all his fruits to Alice and replaces them from the bag
- After processing all cards, the bag must be empty

Find a valid card sequence (compressed format like 3A1B) or 'Impossible'. Format your answer within [answer][/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def vec(a, b):
        return a[0] * b[1] - a[1] * b[0]

    @classmethod
    def check_solution_exists(cls, x, y):
        a = [1, 0]
        b = [0, 1]
        while True:
            sum_a = a[0] + b[0]
            sum_b = a[1] + b[1]
            if sum_a > x or sum_b > y:
                break
            v = [x, y]
            q = cls.vec(a, v)
            w = abs(cls.vec(b, v))
            if q < w:
                c = (w - 1) // q
                b = [b[0] + c * a[0], b[1] + c * a[1]]
            elif q > w:
                c = (q - 1) // w
                a = [a[0] + c * b[0], a[1] + c * b[1]]
            else:
                return sum_a == x and sum_b == y
        return a[0] + b[0] == x and a[1] + b[1] == y

    @staticmethod
    def decompress_solution(solution):
        if solution == 'Impossible':
            return solution
        parts = re.findall(r'(\d+)([AB])', solution)
        if not parts:
            return None
        decompressed = []
        for cnt, c in parts:
            if not cnt.isdigit() or cnt.startswith('0'):
                return None
            count = int(cnt)
            if count < 1:
                return None
            decompressed.append(c * count)
        return ''.join(decompressed) if decompressed else None
