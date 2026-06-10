import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CcelexupdateInstructionGenerator(BaseInstructionGenerator):
    """Ccelexupdate Bootcamp指令生成器"""
    
    def __init__(self, max_x=10**9, max_y=10**9, max_dx=100, max_dy=100):
        """
        初始化Ccelexupdate指令生成器
        
        Args:
            max_x: 参数描述
            max_y: 参数描述
            max_dx: 参数描述
            max_dy: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_x = max_x
        self.max_y = max_y
        self.max_dx = max_dx
        self.max_dy = max_dy
    
    def case_generator(self):
        dx = random.randint(0, self.max_dx)
        x1 = random.randint(1, self.max_x - dx) if dx < self.max_x else 1
        x2 = x1 + dx
        
        dy = random.randint(0, self.max_dy)
        y1 = random.randint(1, self.max_y - dy) if dy < self.max_y else 1
        y2 = y1 + dy
        
        return {
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        x1 = question_case['x1']
        y1 = question_case['y1']
        x2 = question_case['x2']
        y2 = question_case['y2']
        return f"""在Ccelexupdate-2021的GAZ-GIZ函数生成的无限表格中，每个单元格的数值有特定的填充规则。Levian需要你解决一个路径总和计数问题：

任务描述：
从起点({x1},{y1})出发，只能向右或向下移动，到达终点({x2},{y2})。计算所有可能路径中不同元素总和的个数。

规则说明：
1. 路径必须严格向右或向下移动，即每一步只能增加x或y坐标。
2. 多个不同路径可能产生相同的总和，需要统计所有唯一的总和值数量。

示例提示：
当起点为(1,1)，终点为(2,2)时，正确答案是2种不同总和。

请将你的最终答案放置在[answer]和[/answer]标签之间，例如：[answer]5[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

