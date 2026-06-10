import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class ByetanotherarraypartitioningtaskInstructionGenerator(BaseInstructionGenerator):
    """Byetanotherarraypartitioningtask Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, max_m=3, max_k=4):
        """
        初始化Byetanotherarraypartitioningtask指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
        self.max_k = max_k
    
    def case_generator(self):
        for _ in range(1000):  # 防止无限循环，最多尝试1000次
            m = random.randint(1, self.max_m)
            k = random.randint(2, self.max_k)
            if m * k > self.max_n:
                continue
            n = random.randint(m * k, self.max_n)
            a_top = [random.randint(50, 100) for _ in range(m * k)]
            a_rest = [random.randint(-100, 0) for _ in range(n - m * k)]
            a = a_top + a_rest
            random.shuffle(a)
            sum_answer, partitions = self.generate_solution(a, m, k)
            if len(partitions) == k - 1:
                return {
                    'n': n,
                    'm': m,
                    'k': k,
                    'a': a,
                    'sum_answer': sum_answer,
                    'partitions': partitions
                }
        raise ValueError("Unable to generate valid test case after 1000 attempts")
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [
            f"{question_case['n']} {question_case['m']} {question_case['k']}",
            ' '.join(map(str, question_case['a']))
        ]
        input_str = '\n'.join(input_lines)
        return f"""You are a competitive programmer. Solve the subarray partition problem by splitting the array into exactly {question_case['k']} subarrays, each with at least {question_case['m']} elements. The beauty of each subarray is the sum of its {question_case['m']} largest elements. Find the maximum total beauty and the partition points.

Input:
{input_str}

Output the maximum sum on the first line and the partition points (k-1 integers) on the second line. Enclose your answer within [answer] and [/answer]. For example:
[answer]
42
1 3 5
[/answer]
""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_solution(a, m, k):
        asort = sorted(a, reverse=True)
        total_sum = sum(asort[:m * k])
        cut = m * k - 1
        out = []
        currentin = 0
        for i in range(len(a)):
            # 防止cut越界
            if cut >= 0 and a[i] >= asort[cut]:
                if a[i] == asort[cut]:
                    cut -= 1
                currentin += 1
                if currentin == m:
                    out.append(i + 1)
                    currentin = 0
                    if len(out) == k - 1:
                        break
        return total_sum, out
