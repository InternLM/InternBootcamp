import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class CpermutationgameInstructionGenerator(BaseInstructionGenerator):
    """Cpermutationgame Bootcamp指令生成器"""
    
    def __init__(self, n=8):
        """
        初始化Cpermutationgame指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
    
    def case_generator(self):
        n = self.n
        a = list(range(1, n+1))
        random.shuffle(a)
        s = self.compute_s_optimized(n, a)
        return {
            'n': n,
            'a': a,
            's': s
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        prompt = f"""Alice和Bob正在玩一个策略游戏。游戏规则如下：

- 棋盘包含{n}个单元格，按1到{n}编号。每个单元格有一个唯一数字（1到{n}之间）。
- 玩家轮流移动令牌，Alice先手。
- 移动规则：新位置的数字必须严格大于当前数字，且移动距离是当前数字的倍数。
- 无法移动的玩家输。

当前谜题的数组a为：[{', '.join(map(str, a))}]

请针对每个起始位置i（1到{n}），判断Alice获胜的情况。输出一个长度为{n}的字符串，其中第i个字符为'A'（Alice胜）或'B'（Bob胜）。

答案请放在[answer]标签内，例如：[answer]ABAB[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_s_optimized(n, arr):
        pos_map = {num: idx for idx, num in enumerate(arr)}
        moves = [[] for _ in range(n)]

        # 预处理合法移动（优化版本）
        for i in range(n):
            ai = arr[i]
            # 向左遍历（步长ai）
            for j in range(i - ai, -1, -ai):
                if arr[j] > ai:
                    moves[i].append(j)
            # 向右遍历（步长ai）
            for j in range(i + ai, n, ai):
                if arr[j] > ai:
                    moves[i].append(j)

        # 动态规划从后往前处理
        dp = ['B'] * n
        sorted_indices = sorted(range(n), key=lambda x: -arr[x])

        for idx in sorted_indices:
            for move in moves[idx]:
                if dp[move] == 'B':
                    dp[idx] = 'A'
                    break
        return ''.join(dp)
