import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CpetyaandspidersInstructionGenerator(BaseInstructionGenerator):
    """Cpetyaandspiders Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cpetyaandspiders指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，包括棋盘的行数n和列数m，默认为2x3。
        """
        self.n = params.get('n', 2)
        self.m = params.get('m', 3)
    
    def case_generator(self):
        """
        生成一个谜题实例，返回n和m的值以及正确答案max_empty。
        """
        possible_pairs = []
        for n in range(1, 41):
            for m in range(1, 41):
                if n * m <= 40:
                    possible_pairs.append((n, m))
        n, m = random.choice(possible_pairs)
        f_val = self.__compute_f(n, m)
        max_empty = n * m - f_val
        return {
            'n': n,
            'm': m,
            'max_empty': max_empty
        }
    
    @staticmethod
    def prompt_func(question_case):
        """
        将问题实例转换为文本形式的问题。
        """
        n = question_case['n']
        m = question_case['m']
        prompt = (
            f"你有一个{n}×{m}的棋盘，每个格子最初有一个蜘蛛。每秒钟，你可以给每个蜘蛛一个指令，让它们不动或者移动到四个相邻的格子（上下左右）。移动是同时进行的，蜘蛛可以穿过彼此，但不能离开棋盘。在移动后，一些格子可能会有多个蜘蛛，而另一些则可能没有。请计算在最优指令下，棋盘上最多有多少个空的格子。请将答案放在[answer]标签中，例如：[answer]4[/answer]。"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def __compute_f(self, n, m):
        """
        计算函数f(n, m)的值，用于确定最少蜘蛛数。
        """
        if n < m:
            return self.__compute_f(m, n)
        if m == 1:
            return (n + 2) // 3
        elif m == 2:
            return (n + 2) // 2
        elif m == 3:
            return (3 * n + 4) // 4
        elif m == 4:
            if n in {5, 6, 9}:
                return n + 1
            else:
                return n
        elif m == 5:
            if n == 7:
                return (6 * n + 6) // 5
            else:
                return (6 * n + 8) // 5
        elif m == 6:
            if n % 7 == 1:
                return (10 * n + 10) // 7
            else:
                return (10 * n + 12) // 7
        else:
            # 处理m>6的情况，根据问题描述，这可能不会发生
            return 0
