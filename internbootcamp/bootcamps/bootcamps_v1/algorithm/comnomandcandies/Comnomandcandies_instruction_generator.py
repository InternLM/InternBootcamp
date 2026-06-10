import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import random




class ComnomandcandiesInstructionGenerator(BaseInstructionGenerator):
    """Comnomandcandies Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Comnomandcandies指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        # 参数定义：C是总重量限制，Hr是红色糖果的快乐值，Hb是蓝色糖果的快乐值，
        # Wr是红色糖果的重量，Wb是蓝色糖果的重量
        self.params = {
            'C': params.get('C', 10),
            'Hr': params.get('Hr', 3),
            'Hb': params.get('Hb', 5),
            'Wr': params.get('Wr', 2),
            'Wb': params.get('Wb', 3)
        }
    
    def case_generator(self):
        # 生成随机的参数，考虑较大的范围
        C = random.randint(1, 10**9)
        Hr = random.randint(1, 10**9)
        Hb = random.randint(1, 10**9)
        Wr = random.randint(1, 10**9)
        Wb = random.randint(1, 10**9)
        
        # 计算正确解
        max_joy = 0
        max_red = C // Wr if Wr != 0 else 0
        for red in range(0, max_red + 1):
            weight_left = C - red * Wr
            if weight_left < 0:
                continue
            blue = weight_left // Wb if Wb != 0 else 0
            current_joy = red * Hr + blue * Hb
            if current_joy > max_joy:
                max_joy = current_joy
        
        # 返回问题实例
        return {
            'C': C,
            'Hr': Hr,
            'Hb': Hb,
            'Wr': Wr,
            'Wb': Wb,
            'correct_joy': max_joy
        }
    
    @staticmethod
    def prompt_func(question_case):
        prompt = f"""
        你是Om Nom，你有两种糖果可以选择：红色糖果和蓝色糖果。红色糖果每个重{question_case['Wr']}克，能带来{question_case['Hr']}的快乐值；
        蓝色糖果每个重{question_case['Wb']}克，能带来{question_case['Hb']}的快乐值。你最多可以吃{question_case['C']}克的糖果，
        但必须整颗整颗地吃。你的目标是在不超过重量限制的情况下，获得最大的快乐值。
        
        请计算你最多能获得多少快乐值？把答案放在[answer]标签中，例如：
        [answer]16[/answer]
        """
        return prompt.strip() 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

