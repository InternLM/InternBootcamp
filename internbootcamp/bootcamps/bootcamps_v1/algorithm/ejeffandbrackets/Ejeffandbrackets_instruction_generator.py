import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EjeffandbracketsInstructionGenerator(BaseInstructionGenerator):
    """Ejeffandbrackets Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_m=100):
        """
        初始化Ejeffandbrackets指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m // 2) * 2
        a = [random.randint(1, 10) for _ in range(n)]
        b = [random.randint(1, 10) for _ in range(n)]
        return {
            'n': n,
            'm': m,
            'a': a,
            'b': b
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        a = ' '.join(map(str, question_case['a']))
        b = ' '.join(map(str, question_case['b']))
        prompt = f"""Jeff需要绘制一个长度为{n * m}的合法括号序列。每个括号的开闭状态决定消耗的墨水量：

规则：
1. 序列必须合法（正确嵌套）
2. 第i个括号（0索引）若为开括号，消耗a[i%n]升墨水；若为闭，消耗b[i%n]升
3. 参数：n={n}, m={m}（保证总长度是偶数）

输入格式：
{n} {m}
{a}
{b}

请计算最小墨水用量。将最终答案放入[answer]标签内，例如：[answer]42[/answer]"""

        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_ink(n, m, a, b):
        class Uzi:
            def __init__(self):
                self.A = [[float('inf')] * 41 for _ in range(41)]

        def multiply(a_mat, b_mat):
            res = Uzi()
            for i in range(41):
                for j in range(41):
                    min_val = float('inf')
                    for k in range(41):
                        if a_mat.A[i][k] + b_mat.A[k][j] < min_val:
                            min_val = a_mat.A[i][k] + b_mat.A[k][j]
                    res.A[i][j] = min_val
            return res

        G = Uzi()
        for i in range(41):
            dp = [[float('inf')] * 41 for _ in range(n+1)]
            dp[0][i] = 0
            for j in range(1, n+1):
                for k in range(41):
                    if dp[j-1][k] == float('inf'):
                        continue
                    # Open bracket
                    if k < 40:
                        new_k = k + 1
                        cost = a[(j-1) % n]  # Fixed modulo position
                        if dp[j][new_k] > dp[j-1][k] + cost:
                            dp[j][new_k] = dp[j-1][k] + cost
                    # Close bracket
                    if k > 0:
                        new_k = k - 1
                        cost = b[(j-1) % n]  # Fixed modulo position
                        if dp[j][new_k] > dp[j-1][k] + cost:
                            dp[j][new_k] = dp[j-1][k] + cost
            for k in range(41):
                G.A[i][k] = dp[n][k]

        # Matrix exponentiation
        result = Uzi()
        for i in range(41):
            result.A[i][i] = 0
        exponent = m
        current = G
        while exponent > 0:
            if exponent % 2 == 1:
                result = multiply(result, current)
            current = multiply(current, current)
            exponent = exponent // 2
        return result.A[0][0]
