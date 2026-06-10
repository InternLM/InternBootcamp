import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CeverhungrykrakozyabraInstructionGenerator(BaseInstructionGenerator):
    """Ceverhungrykrakozyabra Bootcamp指令生成器"""
    
    def __init__(self, max_L=1000, max_range=100):
        """
        初始化Ceverhungrykrakozyabra指令生成器
        
        Args:
            max_L: 参数描述
            max_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场环境，定义生成范围参数。

        参数:
            max_L (int): 生成左边界L的最大值，默认为1000
            max_range (int): 生成范围的最大跨度(L到R)，默认为100
        """
        self.max_L = max_L
        self.max_range = max_range
    
    def case_generator(self):
        """
        生成符合要求的谜题实例，确保L ≤ R且范围合理
        """
        L = random.randint(1, self.max_L)
        R_max = min(L + self.max_range, 10**18)
        R = random.randint(L, R_max)
        return {'L': L, 'R': R}
    
    @staticmethod
    def prompt_func(question_case):
        """
        将问题实例转换为自然语言描述，包含格式要求
        """
        L = question_case['L']
        R = question_case['R']
        return f"""Slastyona需要喂养Ceverhungrykrakozyabra，这个生物会按以下规则处理数字：
1. 将数字各位排序成非降序（例如57040 → 00457）
2. 去除所有前导零（00457 → 457）
3. 余下部分称为"不可食用尾巴"

请计算范围[{L}, {R}]内所有数字处理后产生的不同尾巴数量。

输出要求：
1. 答案必须是整数
2. 将最终答案放在[answer]和[/answer]之间
示例：[answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

