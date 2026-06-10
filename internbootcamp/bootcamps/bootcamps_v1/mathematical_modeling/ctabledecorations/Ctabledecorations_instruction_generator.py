import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CtabledecorationsInstructionGenerator(BaseInstructionGenerator):
    """Ctabledecorations Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ctabledecorations指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        支持自定义参数：
        - max_val: 气球数量最大值（默认2e9）
        - min_val: 气球数量最小值（默认0）
        """
        super().__init__(**params)
        self.max_val = params.get('max_val', 2000000000)
        self.min_val = params.get('min_val', 0)
    
    def case_generator(self):
        """生成覆盖各种可能边界的测试案例"""
        # 生成基础随机值
        base_params = {
            'r': random.randint(self.min_val, self.max_val),
            'g': random.randint(self.min_val, self.max_val), 
            'b': random.randint(self.min_val, self.max_val)
        }
        
        # 强制包含特殊边界情况
        special_cases = [
            # 两数极大，一数为0
            {'r': self.max_val, 'g': self.max_val, 'b': 0},
            # 三数相等
            {'r': 100, 'g': 100, 'b': 100},
            # 总和不能被3整除
            {'r': 2, 'g': 2, 'b': 2}
        ]
        
        # 随机选择是否包含特殊案例
        if random.random() < 0.2:  # 20%概率生成特殊案例
            return random.choice(special_cases)
        return base_params
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """增强问题描述的严谨性"""
        r = question_case['r']
        g = question_case['g']
        b = question_case['b']
        return f"""As banquet decorator, you must follow these strict rules:
1. Each table requires EXACTLY 3 balloons
2. All 3 balloons CANNOT be the same color
3. Use exactly {r} red, {g} green, {b} blue balloons

Calculate the MAXIMUM number of tables possible. Format your answer as:

[answer]{{number}}[/answer]

Examples:
Input: 5 4 3 → [answer]4[/answer]
Input: 2 3 3 → [answer]2[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

