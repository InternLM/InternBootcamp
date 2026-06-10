import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class F1chessstrikesbackeasyversionInstructionGenerator(BaseInstructionGenerator):
    """F1chessstrikesbackeasyversion Bootcamp指令生成器"""
    
    def __init__(self, max_n=3, max_m=3, max_q=5):
        """
        初始化F1chessstrikesbackeasyversion指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_q: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
        self.max_q = max_q
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        
        # 生成所有合法的白色单元格
        white_cells = []
        for i in range(1, 2*n + 1):
            for j in range(1, 2*m + 1):
                if (i + j) % 2 == 0:
                    white_cells.append((i, j))
        
        # 确定最大可能的q值
        max_possible_q = min(len(white_cells), self.max_q)
        if max_possible_q < 1:
            return {'n': n, 'm': m, 'q': 0, 'queries': [], 'answers': []}
        
        q = random.randint(1, max_possible_q)
        random.shuffle(white_cells)
        queries = [[i, j] for i, j in white_cells[:q]]
        
        answers = self.compute_answers(n, m, queries)
        return {
            'n': n,
            'm': m,
            'q': q,
            'queries': queries,
            'answers': answers,
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        q = question_case['q']
        queries = question_case['queries']
        prompt = f"""Ildar和Ivan正在玩一个基于棋盘的策咯游戏。棋盘的大小为{2*n}行×{2*m}列，其中白色单元格（满足i + j为偶数的位置）可以放置国王。游戏开始时，所有白色单元格都是可用的。

Ildar进行了{q}次操作，每次操作将一个特定的白色单元格标记为不可用。每次操作后，你需要判断是否能够在剩余的可用白色单元格中放置{n*m}个国王，使得这些国王两两之间无法相互攻击（即不能位于相邻的单元格，包括上下、左右以及对角线相邻）。

操作记录如下：
"""
        for idx, (i, j) in enumerate(queries, 1):
            prompt += f"操作{idx}：标记单元格 ({i}, {j}) 为不可用。\n"
        prompt += "\n请针对每个操作后的棋盘状态，依次输出“YES”或“NO”，每个结果占一行，按操作顺序排列，并确保所有结果被包裹在[answer]和[/answer]标签内。例如：\n\n[answer]\nYES\nNO\nYES\n[/answer]\n\n请确保严格按照上述格式要求作答。"
        return prompt.strip() 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_answers(n, m, queries):
        q = len(queries)
        answers = []
        for k in range(1, q + 1):
            f = [-1] * n
            g = [m] * n

            for i, j in queries[:k]:
                s = (i - 1) // 2    # 转换为0-based行号后除2
                t = (j - 1) // 2    # 转换为0-based列号后除2
                # 判断0-based行号的奇偶性
                if (i - 1) % 2 == 1:
                    if t > f[s]:
                        f[s] = t
                else:
                    if t < g[s]:
                        g[s] = t

            # 向右传播f的最大值
            for i in range(n-1, 0, -1):
                if f[i] > f[i-1]:
                    f[i-1] = f[i]

            # 向左传播g的最小值
            for i in range(n-1):
                if g[i] < g[i+1]:
                    g[i+1] = g[i]

            possible = all(g[i] > f[i] for i in range(n))
            answers.append("YES" if possible else "NO")
        return answers
