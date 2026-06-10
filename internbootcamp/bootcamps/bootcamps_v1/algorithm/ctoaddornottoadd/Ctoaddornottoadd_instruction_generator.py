import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
# 无需额外导入

# === 源文件中的全局函数 ===

def compute_max_freq_min_num(n, k, arr):
    arr.sort()
    max_x = 0
    current_sum = 0
    left = 0
    for right in range(n):
        current_sum += arr[right]
        while (right - left + 1) * arr[right] - current_sum > k:
            current_sum -= arr[left]
            left += 1
        current_x = right - left + 1
        if current_x > max_x:
            max_x = current_x

    min_num = float('inf')
    current_sum = 0
    left = 0
    for right in range(n):
        current_sum += arr[right]
        while (right - left + 1) > max_x:
            current_sum -= arr[left]
            left += 1
        if (right - left + 1) == max_x:
            cost = max_x * arr[right] - current_sum
            if cost <= k and arr[right] < min_num:
                min_num = arr[right]
    return (max_x, min_num)


class CtoaddornottoaddInstructionGenerator(BaseInstructionGenerator):
    """Ctoaddornottoadd Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100, min_val=-1000, max_val=1000, max_k=1e6):
        """
        初始化Ctoaddornottoadd指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_val: 参数描述
            max_val: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_val = min_val
        self.max_val = max_val
        self.max_k = max_k
    
    def case_generator(self):
        import random
        n = random.randint(self.min_n, self.max_n)
        k = random.randint(0, int(self.max_k))
        arr = [random.randint(self.min_val, self.max_val) for _ in range(n)]
        max_count, correct_number = compute_max_freq_min_num(n, k, arr)
        return {
            'n': n,
            'k': k,
            'array': arr,
            'max_count': max_count,
            'correct_number': correct_number
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        arr = question_case['array']
        arr_str = ' '.join(map(str, arr))
        problem_text = f"""
You are a programmer and need to solve the following problem. Given an array of {n} integers, you can perform at most {k} operations. In each operation, you can increment an element of the array by 1. Your task is to find the maximum possible number of occurrences of any element after performing at most {k} operations. If multiple elements can achieve this maximum, choose the smallest one among them.

Input format:
- The first line contains two integers n and k.
- The second line contains the array elements separated by spaces.

Output format:
- Two integers separated by a space: the maximum number of occurrences and the smallest element that achieves this maximum.

Please ensure your answer is placed within [answer] and [/answer] tags. For example, if the answer is 3 occurrences for element 4, write [answer]3 4[/answer].

Problem instance:
Input:
{n} {k}
{arr_str}

Please provide your answer as specified."""
        return problem_text.strip() 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

