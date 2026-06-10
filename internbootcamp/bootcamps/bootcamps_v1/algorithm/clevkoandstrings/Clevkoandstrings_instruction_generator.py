import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class ClevkoandstringsInstructionGenerator(BaseInstructionGenerator):
    """Clevkoandstrings Bootcamp指令生成器"""
    
    def __init__(self, max_n=8, max_k=50):
        """
        初始化Clevkoandstrings指令生成器
        
        Args:
            max_n: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_k = max_k  # 允许生成更大的k值
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        max_possible = n * (n + 1) // 2
        # 允许k值覆盖更多边界条件
        k = random.choice([
            0,
            random.randint(1, min(self.max_k, max_possible)),
            min(self.max_k, max_possible)
        ])
        s = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=n))
        return {
            'n': n,
            'k': k,
            's': s,
            'correct_answer': self.compute_answer(n, k, s)
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        s = question_case['s']
        return f"""解决以下编程问题，将答案放入[answer]标签：

给定n={n}, k={k}，字符串s="{s}"，计算满足美丽值为k的字符串t的个数（模10^9+7）。

规则：
1. 美丽值定义为满足t[i..j] > s[i..j]的(i,j)对的数量
2. 比较按字典序进行
3. 结果需要对1000000007取模

示例：
输入：
2 2
yz
输出：
26

你的答案应为一个整数，放在[answer][/answer]标签中。例如：[answer]26[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_answer(n, k, s):
        if k > n*(n+1)//2 or k < 0:
            return 0
        MAX_K = 2000
        k = min(k, MAX_K)

        dp = [[0]*(MAX_K+1) for _ in range(n+1)]
        sum1 = [0]*(MAX_K+1)
        dp[n][0] = 1

        for i in range(n-1, -1, -1):
            new_sum1 = [0]*(MAX_K+1)
            for j in range(MAX_K, -1, -1):
                current = 0

                # Case 1: t[i] < s[i]
                if j <= MAX_K:
                    current += (ord(s[i]) - ord('a')) * dp[i+1][j]

                # Case 2: t[i] > s[i]
                delta = n - i
                if delta <= j <= MAX_K:
                    current += (ord('z') - ord(s[i])) * dp[i+1][j - delta]

                # Case 3: Find first differing position
                used = [False]*(n+1)
                # 处理降序
                for l in range(n-1, i, -1):
                    used[l] = True
                    cnt = (n - l) * (l - i + 1)
                    if cnt > j:
                        break
                    rem = j - cnt
                    if 0 <= rem <= MAX_K:
                        current += (ord('z') - ord(s[l])) * dp[l+1][rem]

                # 处理升序
                for l in range(i+1, n):
                    if used[l]:
                        break
                    cnt = (n - l) * (l - i + 1)
                    if cnt > j:
                        break
                    rem = j - cnt
                    if 0 <= rem <= MAX_K:
                        current += (ord('z') - ord(s[l])) * dp[l+1][rem]

                # Add sum from previous steps
                current += sum1[j]
                if j == 0:
                    current += 1  # 全匹配的情况

                dp[i][j] = current % MOD
                # 更新sum1
                new_sum1[j] = (sum1[j] + (ord(s[i]) - ord('a')) * dp[i+1][j]) % MOD

            sum1 = new_sum1

        return dp[0][k] % MOD
