import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class DrarityandnewdressInstructionGenerator(BaseInstructionGenerator):
    """Drarityandnewdress Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=10):
        """
        初始化Drarityandnewdress指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max(max_n, 1)
        self.max_m = max(max_m, 1)
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        grid = []
        for _ in range(n):
            row = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=m))
            grid.append(row)
        return {'n': n, 'm': m, 'grid': grid}
    
    @staticmethod
    def prompt_func(question_case):
        grid = question_case['grid']
        grid_str = '\n'.join(grid)
        prompt = f"""你是小马谷的服装设计师，需要帮助Rarity计算满足条件的菱形图案数目。布料由{question_case['n']}行{question_case['m']}列的彩色方块组成，每个方块是小写字母表示的顏色。菱形必须满足以下条件：

1. 菱形由同一颜色的方块组成。
2. 菱形的边必须与布料的边成45度角（即呈菱形形状）。
3. 菱形不能超出布料边界。

输入格式：
- 第一行是两个整数n和m。
- 接下来n行，每行m个小写字母。

输出格式：
- 一个整数，表示符合条件的菱形数目。

例如，输入：
3 3
aaa
aaa
aaa
正确输出为10，因为有10个符合条件的菱形。

现在请解决以下谜题实例：
{question_case['n']} {question_case['m']}
{grid_str}

请将最终答案放入[answer]和[/answer]标签之间，例如：[answer]10[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

