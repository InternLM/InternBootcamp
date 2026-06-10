import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class BminimizationInstructionGenerator(BaseInstructionGenerator):
    """Bminimization Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=10, min_k=1, max_k=None, min_val=-100, max_val=100):
        """
        初始化Bminimization指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_k: 参数描述
            max_k: 参数描述
            min_val: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_k = min_k
        self.max_k = max_k
        self.min_val = min_val
        self.max_val = max_val
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        max_k_candidate = min(5000, n - 1)
        if self.max_k is None:
            max_k = max_k_candidate
        else:
            max_k = min(self.max_k, max_k_candidate)
        min_k = max(1, self.min_k)
        max_k = max(min_k, max_k)
        k = random.randint(min_k, max_k)
        A = [random.randint(self.min_val, self.max_val) for _ in range(n)]
        return {
            'n': n,
            'k': k,
            'A': A.copy()
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        A = question_case['A']
        return f"""You are given an array A of {n} integers and a positive integer k. Your task is to find the minimal possible value of S after optimally permuting the array. 

**Problem Details:**
- Array A has the elements: {', '.join(map(str, A))}.
- The integer k is {k}.

**Rules:**
1. Permute the array into any order.
2. Sort the permuted array in non-decreasing order.
3. Split the sorted array into (k+1) consecutive non-empty subarrays by selecting k split points.
4. The sum of the differences at the split points is the sum of the values (first element of next subarray - last element of current subarray) for each split point.
5. The value S is the total range of the sorted array (maximum element - minimum element) minus this sum of differences.

Your goal is to compute the minimal possible value of S.

**Answer Format:**
Place your answer within [answer] and [/answer], like [answer]42[/answer]. Ensure it's the only occurrence and correctly formatted.

Example Answer:
For Input:
3 2
1 2 4
The correct answer is [answer]1[/answer].

Now, solve the following problem:
n = {n}, k = {k}, array A = {A}
What is the minimal possible value of S?""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_sum(n, k, A):
        numbers = sorted(A)
        if n == 0:
            return 0
        if k == 0:
            return numbers[-1] - numbers[0]

        adding_one = n % k
        part_length = n // k
        total_groups = k + 1

        # 构建差分数组（注意索引偏移）
        diff = []
        for i in range(n-1):
            diff.append(numbers[i+1] - numbers[i])

        # 动态规划初始化
        dp = [[0]*(k+1) for _ in range(adding_one+1)]

        # 预处理第一个分割点
        for e in range(1, k+1):
            pos = (e-1)*part_length
            if pos >= len(diff):
                val = 0
            else:
                val = diff[pos]
            dp[0][e] = dp[0][e-1] + val

        # 处理添加额外元素的分割
        for a in range(1, adding_one+1):
            for e in range(1, k+1):
                if e < a: continue
                pos = (e-1)*part_length + a
                if pos >= len(diff):
                    val = 0
                else:
                    val = diff[pos]

                if a == e:
                    dp[a][e] = dp[a-1][e-1] + val
                else:
                    dp[a][e] = max(dp[a-1][e-1], dp[a][e-1]) + val

        max_sum_diff = dp[adding_one][k]
        total_range = numbers[-1] - numbers[0]
        return total_range - max_sum_diff
