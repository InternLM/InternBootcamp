import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CpieordieInstructionGenerator(BaseInstructionGenerator):
    """Cpieordie Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=100, m_min=1, m_max=100, k_min=0, k_max=100):
        """
        初始化Cpieordie指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            m_min: 参数描述
            m_max: 参数描述
            k_min: 参数描述
            k_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(n_min, 1)
        self.n_max = max(n_max, self.n_min)
        self.m_min = max(m_min, 1)
        self.m_max = max(m_max, self.m_min)
        self.k_min = max(k_min, 0)
        self.k_max = max(k_max, self.k_min)
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        m = random.randint(self.m_min, self.m_max)
        k = random.randint(self.k_min, self.k_max)
        pies = []
        answer = 'NO'
        
        if k == 0:
            return {'n':n, 'm':m, 'k':k, 'pies':pies, 'answer':answer}
        
        # Calculate safe zone boundaries
        x_safe_min = 6
        x_safe_max = n - 5
        y_safe_min = 6
        y_safe_max = m - 5
        
        can_no = (x_safe_min <= x_safe_max) and (y_safe_min <= y_safe_max)
        
        if can_no and random.random() < 0.5:
            try:
                pies = [
                    (random.randint(x_safe_min, x_safe_max), 
                     random.randint(y_safe_min, y_safe_max))
                    for _ in range(k)
                ]
                answer = 'NO'
            except ValueError:
                can_no = False
        
        if not can_no:
            danger_pies = []
            for _ in range(k):
                if _ == 0 or random.random() < 0.3:
                    edge = random.choice(['top', 'bottom', 'left', 'right'])
                    if edge in ['top', 'bottom']:
                        x = 1 if edge == 'top' else n
                        y = random.randint(1, m)
                    else:
                        x = random.randint(1, n)
                        y = 1 if edge == 'left' else m
                else:
                    x = random.randint(max(1, n-4), n) if random.random() < 0.5 else random.randint(1, min(5, n))
                    y = random.randint(max(1, m-4), m) if random.random() < 0.5 else random.randint(1, min(5, m))
                danger_pies.append((x, y))
            pies = danger_pies
            answer = 'YES'
        
        return {
            'n': n,
            'm': m,
            'k': k,
            'pies': pies,
            'answer': answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        k = question_case['k']
        pies = question_case['pies']
        prompt = f"""你是Volodya的教练，需要帮助他判断是否能在与Vlad的游戏中获胜。请仔细分析以下棋局并给出答案。

问题描述：

Volodya和Vlad在一个{n}行{m}列的棋盘上进行游戏。棋盘上共有{k}个派，分布在不同的单元格中。每个回合，Volodya可以选择一个派，将其移动到相邻的单元格（上下左右）。如果派位于棋盘的边缘，Volodya可以将其移出棋盘并立即获胜。之后，Vlad会封锁棋盘边缘的一个单位边，阻止之后通过该边移出派。双方都采取最优策略。请判断Volodya是否能确保胜利。

输入格式：

第一行输入三个整数n m k，分别表示棋盘的行数、列数和派的数量。接下来k行，每行两个整数x y，表示派的位置。

你的任务是根据以下输入数据，判断Volodya是否能够获胜，并输出“YES”或“NO”。

输入数据：
{n} {m} {k}"""
        for x, y in pies:
            prompt += f"\n{x} {y}"
        prompt += "\n\n输出要求：\n请将你的答案置于[answer]标签内，例如：[answer]YES[/answer]或[answer]NO[/answer]。确保答案全部大写，并且是唯一的正确选项。"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

