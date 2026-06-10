import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class DmissionimpassableInstructionGenerator(BaseInstructionGenerator):
    """Dmissionimpassable Bootcamp指令生成器"""
    
    def __init__(self, max_length=50, a_positive_prob=0.7):
        """
        初始化Dmissionimpassable指令生成器
        
        Args:
            max_length: 参数描述
            a_positive_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_length = max_length  # 降低默认最大长度
        self.a_positive_prob = a_positive_prob
    
    def case_generator(self):
        l = random.randint(3, self.max_length)
        # 生成包含回文的随机字符串
        core = random.choice(['aa', 'abba', 'abcba', 'aaa'])
        s = core + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=l-len(core)))
        s = ''.join(random.sample(s, len(s)))  # 打乱顺序保持回文可能性
        
        a = []
        for _ in range(l):
            if random.random() < self.a_positive_prob:
                a.append(random.randint(1, 100))
            else:
                a.append(-1)
        return {
            'length': l,
            'a': a,
            's': s[:l]
        }
    
    @staticmethod
    def prompt_func(question_case):
        l = question_case['length']
        a = question_case['a']
        s = question_case['s']
        a_str = ' '.join(map(str, a))
        return f"""根据游戏规则计算字符串{s}的最大可得分值。得分规则：
1. 删除长度为k的回文子串获得a[k-1]分（-1表示禁止删除）
2. 字符串自动拼接后持续删除直到无法操作
3. 输出最大值

输入：
长度：{l}
得分数组：{a_str}
字符串：{s}

将最终答案放在[answer]标签内，如[answer]16[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _compute_max_score(cls, identity):
        s = identity['s']
        a = [x if x != -1 else -float('inf') for x in identity['a']]
        n = len(s)

        # Precompute palindrome table
        is_palin = [[False]*n for _ in range(n)]
        for i in range(n-1, -1, -1):
            for j in range(i, n):
                if i == j:
                    is_palin[i][j] = True
                elif i+1 == j:
                    is_palin[i][j] = (s[i] == s[j])
                else:
                    is_palin[i][j] = (s[i] == s[j] and is_palin[i+1][j-1])

        # Initialize DP tables
        dp = [[-float('inf')]*n for _ in range(n)]
        best = [[0]*n for _ in range(n)]

        for length in range(1, n+1):
            for i in range(n - length +1):
                j = i + length -1
                if length == 1:
                    dp[i][j] = a[0]
                else:
                    # Split into substrings
                    dp[i][j] = max([dp[i][k] + dp[k+1][j] for k in range(i, j)], default=-float('inf'))

                    # Check entire palindrome
                    if is_palin[i][j]:
                        dp[i][j] = max(dp[i][j], a[length-1])

                # Update best solution
                best[i][j] = max(0, dp[i][j])
                for k in range(i, j):
                    best[i][j] = max(best[i][j], best[i][k] + best[k+1][j])

        return best[0][n-1]
