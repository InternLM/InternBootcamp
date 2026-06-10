import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from heapq import heappop
from heapq import heappush




class ClittleelephantandshiftsInstructionGenerator(BaseInstructionGenerator):
    """Clittleelephantandshifts Bootcamp指令生成器"""
    
    def __init__(self, n=5):
        """
        初始化Clittleelephantandshifts指令生成器
        
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
        b = list(range(1, n+1))
        random.shuffle(b)
        expected_output = self.compute_expected(n, a, b)
        return {
            'n': n,
            'a': a,
            'b': b,
            'expected_output': expected_output
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = ' '.join(map(str, question_case['a']))
        b = ' '.join(map(str, question_case['b']))
        prompt = f"""You are a programming competition contestant. Solve the following problem and present your answer in the required format.

Problem Statement:

The Little Elephant has two permutations a and b of length n, where n is a positive integer. The distance between two permutations is defined as the minimum absolute difference between the positions of a common element in a and in some cyclic shift of b. For each of the n cyclic shifts of permutation b, determine the distance to permutation a.

Input Format:

The input consists of:
- The first line contains an integer n, the size of the permutations.
- The second line contains permutation a as n distinct integers separated by spaces.
- The third line contains permutation b in the same format.

Output Format:

Output n lines, each containing one integer. The i-th line should correspond to the distance between permutation a and the i-th cyclic shift of permutation b.

Cyclic Shift Explanation:

A cyclic shift by i (1 ≤ i ≤ n) of permutation b is formed by taking the first i elements and moving them to the end. For example, if b is [3,4,2,1], the 1st cyclic shift is [3,4,2,1], the 2nd is [4,2,1,3], the 3rd is [2,1,3,4], and the 4th is [1,3,4,2].

Examples:

Sample Input 1:
2
1 2
2 1

Sample Output 1:
1
0

Sample Input 2:
4
2 1 3 4
3 4 2 1

Sample Output 2:
2
1
0
1

Your Task:

Compute the distance for each cyclic shift of b and output them in order. Ensure your answer has exactly n lines, each with a single integer. Place your final answer within [answer] tags, like this:

[answer]
<output line 1>
<output line 2>
...
[/answer]

Now, solve the following problem:

Input:
{n}
{a}
{b}

Your answer:
"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_expected(n, a, b):
        # Convert to 0-based and precompute positions in a
        a_pos = {num: idx for idx, num in enumerate(a)}
        ia = [0] * n
        for idx, num in enumerate(a):
            ia[num-1] = idx  # since a contains 1-based numbers

        # Convert b to 0-based indices in b list
        b_zero = [num-1 for num in b]  # to 0-based internally

        ans = [float('inf')] * n
        # Priority queues store (-distance, original index)
        pq_left = []  # elements where i <= ia[b[i]]
        pq_right = []  # elements where i > ia[b[i]]

        for i in range(n):
            current_b = b_zero[i]
            pos_in_a = ia[current_b]
            diff = i - pos_in_a
            if i <= pos_in_a:
                heappush(pq_left, (-(pos_in_a - i), i))
            else:
                heappush(pq_right, (-(i - pos_in_a), i))
            ans[0] = min(ans[0], abs(i - pos_in_a))

        for k in range(1, n):
            # Move elements from previous shift out of the window
            prev_idx = k - 1
            current_b_prev = b_zero[prev_idx]
            pos_in_a_prev = ia[current_b_prev]
            shifted_pos = (prev_idx - (k-1)) % n  # was considered for previous k-1 shifts

            new_diff_for_next = (n - pos_in_a_prev - 1) + k
            heappush(pq_right, (-new_diff_for_next, n + prev_idx))

            # Remove elements from pq_right that are now in pq_left due to shift
            while pq_right and -pq_right[0][0] - k < 0:
                dist, idx = heappop(pq_right)
                new_dist = - (-dist - k)
                heappush(pq_left, (-new_dist, idx))

            # Remove elements from pq_left that are out of the valid indices (>=k)
            while pq_left and pq_left[0][1] < k:
                heappop(pq_left)

            current_min = float('inf')
            if pq_left:
                current_min = min(current_min, -pq_left[0][0] + k)
            if pq_right:
                current_min = min(current_min, -pq_right[0][0] - k)

            ans[k] = current_min

        return ans
