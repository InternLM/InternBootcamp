import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CmarblesInstructionGenerator(BaseInstructionGenerator):
    """Cmarbles Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=20):
        """
        初始化Cmarbles指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.delta = {
            'N': (0, 1),
            'S': (0, -1),
            'E': (1, 0),
            'W': (-1, 0)
        }
    
    def case_generator(self):
        while True:
            n = random.randint(self.n_min, self.n_max)
            path1 = self.generate_valid_path(n-1)
            path2 = self.generate_valid_path(n-1)
            if path1 is not None and path2 is not None:
                return {
                    'n': n,
                    'path1': path1,
                    'path2': path2
                }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        path1 = question_case['path1']
        path2 = question_case['path2']
        prompt = f"""你是Genos，需要帮助判断两个弹珠是否可以同时移动到各自的路径终点。下面是问题的详细说明：

**背景与规则：**

- 两个弹珠分别位于两个不同的网格路径的起点。每个路径的长度为n，由一系列移动方向组成，每个移动方向是N（北）、E（东）、S（南）、W（西）中的一个字符。
- 每次移动时，你必须选择移动其中一个弹珠。另一个弹珠会自动尝试复制相同的移动，但如果无法移动（即该方向无法从当前位置移动到下一个位置），则不会移动。
- 移动只能在路径的相邻位置上进行。也就是说，弹珠只能沿路径的步进顺序移动，不能跳过或回退到之前的位置，除了自动复制移动的情况。
- 输入的路径保证不会出现三个连续的步骤导致坐标交替出现的情况（例如A → B → A的结构）。

**输入：**

- 第一行是整数n（2 ≤ n ≤ 1,000,000），表示路径的长度。
- 第二行是第一个路径的移动序列，由n-1个字符组成。
- 第三行是第二个路径的移动序列，同样有n-1个字符。

**任务：**

判断是否存在一种移动顺序，使得两个弹珠最终同时停留在各自的终点。如果是，输出“YES”；否则，输出“NO”。

**当前问题实例：**

n = {n}

第一个路径的移动序列：{path1}

第二个路径的移动序列：{path2}

**答案格式要求：**

请将最终答案用[answer]标签包裹，例如：[answer]YES[/answer]或[answer]NO[/answer]。确保只包含一个答案，并且是最后一次判断的结果。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_valid_path(self, length):
        directions = ['N', 'E', 'S', 'W']
        pos = [(0, 0)]
        path = []
        for _ in range(length):
            available = []
            current_pos = pos[-1]
            if len(pos) >= 2:
                prev_prev_pos = pos[-2]
                for d in directions:
                    dx, dy = self.delta[d]
                    new_x = current_pos[0] + dx
                    new_y = current_pos[1] + dy
                    new_pos = (new_x, new_y)
                    if new_pos != prev_prev_pos:
                        available.append(d)
            else:
                available = directions.copy()
            if not available:
                return None
            d = random.choice(available)
            dx, dy = self.delta[d]
            new_pos = (current_pos[0] + dx, current_pos[1] + dy)
            pos.append(new_pos)
            path.append(d)
        return ''.join(path)
