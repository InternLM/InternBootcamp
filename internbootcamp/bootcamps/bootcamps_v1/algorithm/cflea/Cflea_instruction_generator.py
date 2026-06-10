import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CfleaInstructionGenerator(BaseInstructionGenerator):
    """Cflea Bootcamp指令生成器"""
    
    def __init__(self, max_dim=10**6):
        """
        初始化Cflea指令生成器
        
        Args:
            max_dim: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_dim = max_dim
    
    def case_generator(self):
        s = random.choice([
            random.randint(1, self.max_dim),
            random.randint(self.max_dim//2, self.max_dim),
            1
        ])
        n = random.choice([
            random.randint(1, 10),
            random.randint(1, self.max_dim),
            self.max_dim
        ])
        m = random.choice([
            random.randint(1, 10),
            random.randint(1, self.max_dim),
            self.max_dim
        ])
        return {'n': n, 'm': m, 's': s}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        s = question_case['s']
        problem_text = f"""你是Berland棋盘上的一只跳蚤，棋盘的大小是{n}厘米（长）x {m}厘米（宽），每个单元格是1x1厘米。你只能在水平或垂直方向上跳跃，每次跳跃的长度固定为s厘米。你希望找出有多少个起始位置(x,y)使得可达的单元格数目是所有起始位置中的最大值。

规则说明：
1. 棋盘共有n×m个单元格，坐标范围为(1 ≤ x ≤ n, 1 ≤ y ≤ m)
2. 每次跳跃必须为s厘米，且在水平或垂直方向，可跳跃任意次数（包括0次）
3. 不能跳出棋盘边界，允许多次访问同一单元格
4. dx,y表示从(x,y)出发可达的单元格总数
5. 你需要计算具有最大dx,y值的起始位置数量

输入参数：
n = {n}
m = {m}
s = {s}

请将最终答案放在[answer]标签内，例如：[answer]42[/answer]。"""
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

