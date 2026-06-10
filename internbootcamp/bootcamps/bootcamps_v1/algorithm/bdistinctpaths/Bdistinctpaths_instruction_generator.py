import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class BdistinctpathsInstructionGenerator(BaseInstructionGenerator):
    """Bdistinctpaths Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Bdistinctpaths指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 2)
        self.m = params.get('m', 2)
        self.k = params.get('k', 4)
    
    def case_generator(self):
        # 生成n和m，确保required_k <= 10
        while True:
            n = random.randint(1, 1000)
            m = random.randint(1, 1000)
            required_k = n + m - 1
            if required_k <= 10:
                break
        k = random.randint(required_k, 10)
        board = [[0 for _ in range(m)] for _ in range(n)]
        # 确保至少有1个颜色已经涂色
        for i in range(random.randint(0, 5)):
            x = random.randint(0, n-1)
            y = random.randint(0, m-1)
            color = random.randint(1, k)
            board[x][y] = color
        return {
            'n': n,
            'm': m,
            'k': k,
            'board': board
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        k = question_case['k']
        board = question_case['board']
        board_str = '\n'.join([' '.join(map(str, row)) for row in board])
        prompt = f"你有一个{n}×{m}的棋盘，每个格子可能已经涂色或未涂色。你需要将所有未涂色的格子涂上颜色（颜色编号为1到{k}），满足以下规则：\n\n"
        prompt += "规则：任何一条从左上角到右下角的路径只能向右或向下移动，并且路径上的所有格子的颜色必须互不相同。\n\n"
        prompt += "棋盘的初始状态如下：\n\n"
        prompt += board_str + "\n\n"
        prompt += "请计算满足条件的涂色方案数，并将答案放在[answer]标签内，格式为：[answer]数字[/answer]。"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

