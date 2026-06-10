import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CvaleraandtubesInstructionGenerator(BaseInstructionGenerator):
    """Cvaleraandtubes Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=10, min_m=2, max_m=10):
        """
        初始化Cvaleraandtubes指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_m = min_m
        self.max_m = max_m
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        m = random.randint(self.min_m, self.max_m)
        max_k = (n * m) // 2
        k = random.randint(1, max_k)
        return {
            'n': n,
            'm': m,
            'k': k
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        k = question_case['k']
        prompt = f"""你是一名网格谜题解决专家。Valera有一个{n}行{m}列的矩形网格，他需要在这个网格上放置{k}个管子。每个管子由一系列相邻的网格单元格组成，具体要求如下：

1. 每个管子必须是一个连续的单元格序列，相邻单元格之间上下或左右相邻（即曼哈顿距离为1）。
2. 每个管子至少包含2个单元格，且每个单元格在管子中只能出现一次。
3. 所有{k}个管子必须完全覆盖网格的所有单元格，且管子之间不能有任何重叠。

请编写一个程序，按照以下格式输出解决方案：

- 输出{k}行，每行描述一个管子。
- 每行的格式为：首先是一个整数r_i表示该管子的单元格数量，接着是2*r_i个整数，依次表示每个单元格的x坐标和y坐标（按照管子从起点到终点的顺序排列）。

示例输入（n=3, m=3, k=3）的输出可能为：

[answer]
3 1 1 1 2 1 3
3 2 1 2 2 2 3
3 3 1 3 2 3 3
[/answer]

注意：
- x的范围是1到{n}，y的范围是1到{m}。
- 确保每个单元格被恰好一个管子使用，且所有管子遵守相邻规则。
- 将你的答案放置在[answer]和[/answer]标签之间。

请解决以下具体问题：
n = {n}, m = {m}, k = {k}
"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

