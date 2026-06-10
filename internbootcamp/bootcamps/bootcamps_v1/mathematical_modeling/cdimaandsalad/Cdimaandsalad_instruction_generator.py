import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
from collections import defaultdict
import random

# === 源文件中的全局函数 ===

def solve(n, k, a_list, b_list):
    b = [x * k for x in b_list]
    b2t = defaultdict(int)
    b2t[0] = 0
    for t, c in zip(a_list, b):
        bal = t - c
        updates = {}
        for ba in list(b2t.keys()):
            new_ba = ba + bal
            new_ta = b2t[ba] + t
            if new_ta > updates.get(new_ba, 0):
                updates[new_ba] = new_ta
        for key, val in updates.items():
            if val > b2t.get(key, 0):
                b2t[key] = val
    max_taste = b2t.get(0, 0)
    return max_taste if max_taste != 0 else -1


class CdimaandsaladInstructionGenerator(BaseInstructionGenerator):
    """Cdimaandsalad Bootcamp指令生成器"""
    
    def __init__(self, max_n=100, k_min=1, k_max=10):
        """
        初始化Cdimaandsalad指令生成器
        
        Args:
            max_n: 参数描述
            k_min: 参数描述
            k_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.k_min = k_min
        self.k_max = k_max
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        k = random.randint(self.k_min, self.k_max)
        
        # Generate valid parameters with guaranteed solution
        valid_case = random.choice([True, False])
        if valid_case:
            # Generate at least one valid fruit
            a = []
            b = []
            # Ensure at least one valid fruit exists
            bi_valid = random.randint(1, 100)
            a.append(k * bi_valid)
            b.append(bi_valid)
            
            # Generate remaining fruits
            for _ in range(n-1):
                if random.random() < 0.3:  # 30% chance to generate valid fruits
                    bi = random.randint(1, 100)
                    ai = k * bi
                else:
                    bi = random.randint(1, 100)
                    ai = random.randint(1, 100)
                a.append(ai)
                b.append(bi)
        else:
            # Generate fruits with all a_i != k*b_i
            while True:
                a = [random.randint(1, 100) for _ in range(n)]
                b = [random.randint(1, 100) for _ in range(n)]
                if not any(a[i] == k * b[i] for i in range(n)):
                    break

        expected_output = solve(n, k, a, b)
        return {
            'n': n,
            'k': k,
            'a': a,
            'b': b,
            'expected_output': expected_output
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        k = question_case['k']
        a = ' '.join(map(str, question_case['a']))
        b = ' '.join(map(str, question_case['b']))
        return f"""你需要解决一个水果沙拉组合优化问题：

题目要求：
从n个水果中选择至少一个，使得总味道与总卡路里的比值正好等于k，且总味道最大。如果无解则返回-1。

输入格式：
第一行：两个整数n和k（用空格分隔）
第二行：{n}个整数表示水果的味道值
第三行：{n}个整数表示水果的卡路里

当前测试案例：
{n} {k}
{a}
{b}

请逐步思考并给出最终答案，格式为：[answer]答案[/answer]。例如：[answer]18[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

