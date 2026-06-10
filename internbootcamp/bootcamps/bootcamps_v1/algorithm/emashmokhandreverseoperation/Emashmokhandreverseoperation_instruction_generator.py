import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EmashmokhandreverseoperationInstructionGenerator(BaseInstructionGenerator):
    """Emashmokhandreverseoperation Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_m=5, min_val=1, max_val=100):
        """
        初始化Emashmokhandreverseoperation指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            min_val: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
        self.min_val = min_val
        self.max_val = max_val
    
    def case_generator(self):
        n = random.randint(0, self.max_n)
        size = 2 ** n
        a = [random.randint(self.min_val, self.max_val) for _ in range(size)]
        m = random.randint(1, self.max_m)
        queries = [random.randint(0, n) for _ in range(m)]
        
        # Precompute inversion layers using reference solution approach
        current_a = a.copy()
        f = {i: [0, 0] for i in range(n+1)}  # Layer inversion counts
        
        def build(l, r, h):
            if l >= r: return
            mid = (l + r) // 2
            build(l, mid, h+1)
            build(mid+1, r, h+1)
            
            inv0 = 0
            inv1 = 0
            i, j = l, mid+1
            merged = []
            while i <= mid and j <= r:
                if current_a[i] <= current_a[j]:
                    merged.append(current_a[i])
                    inv1 += j - (mid+1)
                    i += 1
                else:
                    merged.append(current_a[j])
                    inv0 += i - l
                    j += 1
            
            while i <= mid:
                merged.append(current_a[i])
                inv1 += r - mid
                i += 1
                
            while j <= r:
                merged.append(current_a[j])
                inv0 += mid - l + 1
                j += 1
                
            for k in range(l, r+1):
                current_a[k] = merged[k-l]
            
            f[h][0] = inv0
            f[h][1] = inv1
        
        if n > 0:
            build(0, len(current_a)-1, 0)
        
        # Precompute initial total inversions
        total_inversions = sum(f[layer][1] for layer in f)
        
        answers = []
        for q in queries:
            # Apply query transformation by flipping layers
            layers_to_flip = [n - q] if q != 0 else []
            if q > 0:
                layers_to_flip += list(range(n - q + 1, n + 1))
            
            for layer in layers_to_flip:
                total_inversions -= f[layer][1]
                f[layer][0], f[layer][1] = f[layer][1], f[layer][0]
                total_inversions += f[layer][1]
            
            answers.append(total_inversions)
        
        return {
            'n': n,
            'a': a,
            'queries': queries,
            'answers': answers
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a_str = ', '.join(map(str, question_case['a']))
        queries_str = ', '.join(map(str, question_case['queries']))
        m = len(question_case['queries'])
        prompt = f"""You are participating in an ACM programming contest. Your task is to process {m} queries on an array. Each query requires you to split the array into subarrays, reverse each, and compute the inversion count.

The initial array a has length 2^{question_case['n']} and is: [{a_str}].

There are {m} queries: {queries_str}.

For each query q_i (which is an integer value):
1. Split the array into 2^(n - q_i) subarrays, each of size 2^q_i, where n is {question_case['n']}
2. Reverse each subarray
3. Combine all reversed subarrays in the same order
4. Compute the number of inversions in the new array

Output your answers as {m} lines inside [answer] tags. Example:
[answer]
0
6
6
0
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

