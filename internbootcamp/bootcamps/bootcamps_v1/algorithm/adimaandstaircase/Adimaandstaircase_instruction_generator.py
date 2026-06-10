import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class AdimaandstaircaseInstructionGenerator(BaseInstructionGenerator):
    """Adimaandstaircase Bootcamp指令生成器"""
    
    def __init__(self, max_stairs=10, max_boxes=10, max_height=10**9):
        """
        初始化Adimaandstaircase指令生成器
        
        Args:
            max_stairs: 参数描述
            max_boxes: 参数描述
            max_height: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_stairs = max_stairs
        self.max_boxes = max_boxes
        self.max_height = max_height
    
    def case_generator(self):
        n = random.randint(1, self.max_stairs)
        a = [random.randint(1, self.max_height) for _ in range(n)]
        a.sort()
        m = random.randint(1, self.max_boxes)
        boxes = []
        for _ in range(m):
            wi = random.randint(1, n)
            hi = random.randint(1, self.max_height)
            boxes.append([wi, hi])
        return {
            'n': n,
            'a': a,
            'm': m,
            'boxes': boxes
        }
    
    @staticmethod
    def prompt_func(question_case):
        a_str = ' '.join(map(str, question_case['a']))
        boxes = question_case['boxes']
        boxes_str = '\n'.join(f"{w} {h}" for w, h in boxes)
        prompt = f"""Dima有一个由{question_case['n']}个台阶组成的楼梯，各台阶初始高度依次为：{a_str}。接下来抛下{question_case['m']}个盒子，每个盒子的宽度和高度如下：
{boxes_str}

每个盒子的底部会落在前w个台阶上，下落后将停留在当前最高的平台（可能是台阶顶或之前的盒子顶）。请按顺序输出每个盒子落地后的底部高度。

答案应为一个包含{question_case['m']}个整数的列表，每个整数对应一个盒子的结果，按输入顺序排列，每个数占一行，并放置在[answer]和[/answer]标签之间。

例如，输出格式应为：
[answer]
答案1
答案2
...
[/answer]
请确保答案准确无误，并严格遵循上述格式。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

