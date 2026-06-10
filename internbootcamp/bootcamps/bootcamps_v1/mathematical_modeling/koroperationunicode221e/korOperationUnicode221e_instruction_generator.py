import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class Koroperationunicode221eInstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode221e Bootcamp指令生成器"""
    
    def __init__(self, max_num=10, solve_ratio=0.5):
        """
        初始化Koroperationunicode221e指令生成器
        
        Args:
            max_num: 参数描述
            solve_ratio: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_num = max_num
        self.solve_ratio = solve_ratio
    
    def case_generator(self):
        """增强案例生成逻辑，保证数值有效性"""
        if random.random() < self.solve_ratio:
            var_type = random.choice(['x', 'y'])
            if var_type == 'x':
                while True:
                    b = random.randint(1, self.max_num)
                    x = random.randint(1, self.max_num)
                    c = x**2 + b**2
                    # 确保解在允许范围内
                    valid_solutions = [
                        i for i in range(1, self.max_num+1)
                        if i**2 + b**2 == c
                    ]
                    if len(valid_solutions) == 1:
                        return {"problem_type": "solve_x", "b": b, "c": c}
            else:
                while True:
                    a = random.randint(1, self.max_num)
                    y = random.randint(1, self.max_num)
                    c = a**2 + y**2
                    valid_solutions = [
                        i for i in range(1, self.max_num+1)
                        if a**2 + i**2 == c
                    ]
                    if len(valid_solutions) == 1:
                        return {"problem_type": "solve_y", "a": a, "c": c}
        else:
            # 允许生成相同的a和b
            a = random.randint(1, self.max_num)
            b = random.randint(1, self.max_num)
            return {"problem_type": "compute", "a": a, "b": b}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        problem_templates = {
            "compute": "计算 {a}∞{b} 的结果。答案格式示例：[[13]]",
            "solve_x": "解方程 X∞{b} = {c}。答案格式示例：[[2]]",
            "solve_y": "解方程 {a}∞Y = {c}。答案格式示例：[[3]]"
        }
        template = """请根据以下规则解决问题：
- 运算符定义：a∞b = a² + b²
- 所有变量均为正整数

当前问题：
{problem_statement}

请将最终答案放在双括号内，如：[[答案]]"""
        
        return template.format(
            problem_statement=problem_templates[question_case["problem_type"]].format(**question_case)
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

