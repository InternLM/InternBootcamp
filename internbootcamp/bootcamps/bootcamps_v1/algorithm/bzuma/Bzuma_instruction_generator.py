import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class BzumaInstructionGenerator(BaseInstructionGenerator):
    """Bzuma Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Bzuma指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = params.get('min_n', 1)
        self.max_n = params.get('max_n', 10)
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        colors = self._generate_valid_colors(n)
        min_steps = self._calculate_min_steps(colors)
        return {
            'n': n,
            'colors': colors,
            'min_steps': min_steps
        }
    
    @staticmethod
    def prompt_func(question_case):
        colors = question_case['colors']
        example = """
示例1：
输入：3
      1 2 1
输出：1（直接消除整个回文）

示例2：
输入：3
      1 2 3 
输出：3（每次只能消除一个）"""
        return f"""祖玛游戏问题：给定{question_case['n']}个宝石组成的序列{colors}，
每次可以消除一个连续回文子串，求完全消除需要的最少次数。

规则说明：
1. 回文子串长度至少为1
2. 消除操作后剩余宝石会自动合并
3. 需保证策略最优性

请给出准确的最小操作次数，答案用[answer]标签包裹，如：[answer]2[/answer]。
{example}""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_colors(self, n):
        """生成至少有一个回文子串的合法颜色序列"""
        colors = []
        for _ in range(n):
            # 50%概率延续当前颜色形成回文
            if colors and random.random() < 0.3:
                colors.append(random.choice(colors))
            else:
                colors.append(random.randint(1, n))
        return colors

    def _calculate_min_steps(self, colors):
        n = len(colors)
        if n == 0:
            return 0

        dp = [[0]*n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 1

        for ln in range(1, n):
            for i in range(n - ln):
                j = i + ln
                dp[i][j] = min(dp[i][k] + dp[k+1][j] for k in range(i, j))

                if colors[i] == colors[j]:
                    if ln == 1:
                        dp[i][j] = 1
                    else:
                        dp[i][j] = min(dp[i][j], dp[i+1][j-1])

        return dp[0][n-1]
