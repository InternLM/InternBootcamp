import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class DzumaInstructionGenerator(BaseInstructionGenerator):
    """Dzuma Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=15, color_range=5):
        """
        初始化Dzuma指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            color_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.color_range = color_range
    
    def case_generator(self):
        """生成任意随机序列，确保包含各类测试案例"""
        n = random.randint(self.min_n, self.max_n)
        colors = [random.randint(1, self.color_range) for _ in range(n)]
        expected = self._compute_min_steps(colors)
        return {'n': n, 'colors': colors, 'expected': expected}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        colors = ' '.join(map(str, question_case['colors']))
        return f"""在祖玛游戏中，你需要消除一行宝石。规则如下：
1. 每步可消除一个连续回文子串
2. 回文指正读反读相同的序列
当前宝石序列（共{question_case['n']}个）：{colors}
请输出最少需要多少秒，将答案放在[answer][/answer]中。如：[answer]2[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_min_steps(colors):
        """动态规划算法重构版"""
        n = len(colors)
        dp = [[0]*n for _ in range(n)]

        for i in range(n-1, -1, -1):
            for j in range(i, n):
                if i == j:
                    dp[i][j] = 1
                    continue

                # 基准情况：逐个消除
                dp[i][j] = dp[i][j-1] + 1

                # 处理相同颜色相邻的情况
                if colors[j] == colors[j-1]:
                    dp[i][j] = min(dp[i][j], dp[i][j-2] + 1 if j-2 >= i else 1)

                # 遍历所有可能的分割点
                for k in range(i, j):
                    if colors[k] == colors[j]:
                        dp[i][j] = min(dp[i][j], dp[i][k] + (dp[k+1][j-1] if k+1 <= j-1 else 0))

                # 处理端点相同的情况
                if colors[i] == colors[j]:
                    if j - i > 1:
                        dp[i][j] = min(dp[i][j], dp[i+1][j-1])
                    else:
                        dp[i][j] = 1
        return dp[0][n-1]
