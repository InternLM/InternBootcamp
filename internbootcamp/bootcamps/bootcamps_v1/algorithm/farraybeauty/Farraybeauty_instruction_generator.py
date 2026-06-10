import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from bisect import bisect_right

# === 源文件中的全局变量 ===

MOD = 998244353

INF = 10**18


class FarraybeautyInstructionGenerator(BaseInstructionGenerator):
    """Farraybeauty Bootcamp指令生成器"""
    
    def __init__(self, min_n=5, max_n=10, min_k=3, min_a=0, max_a=100):
        """
        初始化Farraybeauty指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_k: 参数描述
            min_a: 参数描述
            max_a: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        调整默认参数以确保验证效率：
        - 限制数组长度范围5-10
        - 限制元素数值范围0-100
        - 要求k至少为3以控制循环次数
        """
        self.min_n = min_n
        self.max_n = max_n
        self.min_k = min_k
        self.min_a = min_a
        self.max_a = max_a
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        k = random.randint(max(self.min_k, 3), n)  # 保证k至少为3减少循环次数
        a = [random.randint(self.min_a, self.max_a) for _ in range(n)]
        return {
            "n": n,
            "k": k,
            "a": a.copy()
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        problem = f"""You are given an array of integers and need to calculate the sum of beauty values for all subsequences of length exactly k. The result must be modulo 998244353.

Problem Description:
- Original array elements: {', '.join(map(str, question_case['a']))}
- Array length (n): {question_case['n']}
- Subsequence length (k): {question_case['k']}

Rules:
1. A subsequence is formed by deleting elements while maintaining order
2. Beauty is the minimum absolute difference between any two elements in the subsequence
3. Consider ALL possible subsequences of length EXACTLY k
4. Output the sum modulo 998244353

Note: The array elements may not be sorted. The minimal valid k is 3.

Format your final numerical answer within [answer] and [/answer] tags."""

        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_answer(n, k, original_a):
        """优化后的计算逻辑，添加了提前终止条件和范围优化"""
        if k < 2:
            return 0

        sorted_a = sorted(original_a)
        max_diff = sorted_a[-1] - sorted_a[0]
        max_x = max_diff // (k-1) if k > 1 else 0

        # 调整循环范围为实际可能的最小值
        M = min(10**5 + 5, max_x + 2) if max_x else 10**5 + 5
        a = [-INF] + sorted_a
        ans = 0

        for x in range(1, M + 1):
            if x * (k-1) > M:
                break

            # 预处理指针数组
            l = [0]*(n+1)
            for i in range(1, n+1):
                target = a[i] - x
                l[i] = bisect_right(a, target, 0, i) - 1
                l[i] = max(l[i], l[i-1])

            # 动态规划部分
            dp = [[0]*(n+1) for _ in range(k+1)]
            dp[0][0] = 1

            for i in range(k):
                prefix = [0]*(n+1)
                prefix[0] = dp[i][0]
                for j in range(1, n+1):
                    prefix[j] = (prefix[j-1] + dp[i][j]) % MOD

                for j in range(1, n+1):
                    if l[j] >= 0:
                        dp[i+1][j] = prefix[l[j]] % MOD

            res = sum(dp[k][j] for j in range(1, n+1)) % MOD
            ans = (ans + res) % MOD

        return ans
