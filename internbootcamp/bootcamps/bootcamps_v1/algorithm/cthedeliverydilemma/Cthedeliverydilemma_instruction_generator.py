import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re




class CthedeliverydilemmaInstructionGenerator(BaseInstructionGenerator):
    """Cthedeliverydilemma Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, a_max=10**9, b_max=10**9):
        """
        初始化Cthedeliverydilemma指令生成器
        
        Args:
            max_n: 参数描述
            a_max: 参数描述
            b_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.a_max = a_max
        self.b_max = b_max
    
    def case_generator(self):
        import random
        n = random.randint(1, self.max_n)
        # 保证生成的a和b包含全配送/全自取等边界情况
        a = [random.randint(1, self.a_max) for _ in range(n)]
        b = [random.randint(1, self.b_max) for _ in range(n)]
        # 强制添加一个b总和极小的案例
        if random.random() < 0.2:
            b = [1] * n
        return {'n': n, 'a': a, 'b': b}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        prompt = (
            "Petya需要订购n道不同的菜肴。每道菜可以选择由餐厅配送或自己取。配送的餐厅会同时派送，总配送时间取其中的最大值。自己取的餐厅需要依次前往，总时间是它们的累计值。最终总时间为配送时间的最大值与自己取的时间总和的较大者。\n\n"
            "输入格式：\n"
            "第一行是n，表示菜肴数量。\n"
            "第二行是n个整数a_i，表示配送时间。\n"
            "第三行是n个整数b_i，表示自取时间。\n\n"
            "当前测试用例：\n"
            f"n = {question_case['n']}\n"
            f"a = {question_case['a']}\n"
            f"b = {question_case['b']}\n\n"
            "请输出一个整数，表示所有可能方案中的最小总时间，并将其包裹在[answer]和[/answer]标签内，例如：[answer]5[/answer]。\n"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_time(n, a, b):
        sorted_pairs = sorted(zip(a, b), key=lambda x: x[0])
        total_b = sum(b)
        prefix_b = [0]
        for a_i, b_i in sorted_pairs:
            prefix_b.append(prefix_b[-1] + b_i)
        min_time = total_b  # 初始化为全自取的情况
        for i in range(n):
            current_a = sorted_pairs[i][0]
            remaining_b = total_b - prefix_b[i+1]
            min_time = min(min_time, max(current_a, remaining_b))
        return min_time
