import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import itertools
import random
import re




class DominosaInstructionGenerator(BaseInstructionGenerator):
    """Dominosa Bootcamp指令生成器"""
    
    def __init__(self, n=4):
        """
        初始化Dominosa指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化Dominosa训练场环境，配置数字范围和网格参数。

        参数:
            n: 数字范围上限，生成数字0-n的连续集合，默认4对应5x6网格
        """
        self.n = n
        self.rows = n + 1
        self.cols = n + 2
    
    def case_generator(self):
        """
        生成合法Dominosa谜题实例，保证至少存在一个解。
        
        返回:
            dict: 包含网格布局和参数的字典，结构为{'grid': 二维列表, 'n': 数字范围}
        """
        # 生成所有可能的无序数字对并打乱顺序
        pairs = list(itertools.combinations_with_replacement(range(self.n + 1), 2))
        random.shuffle(pairs)
        # 创建网格并填充数字对
        grid = []
        pair_index = 0
        if self.cols % 2 == 0:
            for i in range(self.rows):
                row = []
                for j in range(0, self.cols, 2):
                    a, b = pairs[pair_index]
                    row.extend([a, b])  # 水平排列数字对
                    pair_index += 1
                grid.append(row)
        else:
            grid = [[] for _ in range(self.rows)]
            for i in range(0, self.cols):
                for j in range(0, self.rows, 2):
                    a, b = pairs[pair_index]
                    grid[j].append(a)
                    grid[j+1].append(b)
                    pair_index += 1

        return {
            'grid': grid,
            'n': self.n
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        将数字网格转化为自然语言问题描述，包含格式说明。
        
        参数:
            question_case: case_generator生成的谜题实例
            
        返回:
            str: 包含网格布局和解答要求的提示文本
        """
        grid = question_case['grid']
        n = question_case['n']
        
        prompt = f"""你是Dominosa谜题专家，请将以下{len(grid)}x{len(grid[0])}网格划分为不重复的骨牌组合。每个骨牌必须覆盖两个相邻单元格（水平或垂直），且所有数字对唯一。

网格布局（行号从0开始）：
"""
        for i, row in enumerate(grid):
            prompt += f"行{i}:\t" + "\t".join(map(str, row)) + "\n"

        prompt += f"""
规则说明：
1. 数字范围：0-{n}，每个骨牌包含两个不同或相同的数字
2. 数对(a,b)与(b,a)视为相同，必须唯一
3. 必须完全覆盖所有单元格

答案格式要求：
将每个骨牌表示为两个坐标对，每行一个骨牌，如：
[answer]
(行号,列号),(行号,列号)
...[/answer]

请确保：
- 使用英文括号和逗号
- 按最后出现的答案块评分
- 坐标按行号、列号顺序"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

