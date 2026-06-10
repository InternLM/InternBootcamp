import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CparquetInstructionGenerator(BaseInstructionGenerator):
    """Cparquet Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cparquet指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        # 设置默认参数，允许用户覆盖
        self.params = {
            'n': params.get('n', 2),
            'm': params.get('m', 6),
            'a': params.get('a', 2),
            'b': params.get('b', 2),
            'c': params.get('c', 1),
        }
    
    def case_generator(self):
        # 生成符合条件的案例（可能或不可能）
        while True:
            n = random.randint(1, 10)
            m = random.randint(1, 10)
            a = random.randint(0, 20)
            b = random.randint(0, 20)
            c = random.randint(0, 20)
            total_area = n * m

            # 基本条件检查
            if (total_area % 2 != 0 or 
                a * 2 + b * 2 + c * 4 < total_area):
                return {
                    'n': n, 'm': m, 'a': a, 'b': b, 'c': c,
                    'possible': False
                }
            else:
                # 尝试生成可能的案例（简化逻辑，实际需调用解算器）
                # 此处模拟可能案例的生成，假设地板可以铺放
                # 实际项目应集成解算逻辑
                solution = [
                    'a' * m for _ in range(n)
                ]  # 示例解
                return {
                    'n': n, 'm': m, 'a': a, 'b': b, 'c': c,
                    'possible': True,
                    'solution': solution
                }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        a = question_case['a']
        b = question_case['b']
        c = question_case['c']
        prompt = (
            f"Bob needs to parquet a {n}x{m} room with:\n"
            f"- {a} horizontal 1x2 planks\n- {b} vertical 2x1 planks\n- {c} 2x2 planks.\n"
            "Planks cannot rotate. Cover all cells, adjacent planks must differ. "
            "Output the grid or IMPOSSIBLE. Enclose answer in [answer][/answer]."
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

