import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EalyonaandtowersInstructionGenerator(BaseInstructionGenerator):
    """Ealyonaandtowers Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ealyonaandtowers指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        # 扩展参数范围，支持更大规模测试案例生成
        self.n_max = params.get('n_max', 10)  # 测试时可适当增大，但保持验证可行性
        self.d_max = params.get('d_max', 10)
        self.a_max = params.get('a_max', 10)
        # 保持其他参数的默认范围限制以确保暴力验证可行

        # 继承其他参数设置...
        self.n_min = params.get('n_min', 1)
        self.m_min = params.get('m_min', 1)
        self.m_max = params.get('m_max', 5)
        self.d_min = params.get('d_min', 1)
        self.a_min = params.get('a_min', 1)
    
    def case_generator(self):
        # 保证生成的案例有独特结构以形成有效山脉
        n = random.randint(self.n_min, self.n_max)
        
        # 生成初始数组时增加峰形结构的概率
        if random.random() < 0.7 and n > 2:
            # 生成峰形结构
            peak = random.randint(1, n-2)
            a = [random.randint(1, 5) for _ in range(n)]
            for i in range(peak):
                a[i+1] = a[i] + random.randint(1, 3)
            for i in range(peak, n-1):
                a[i+1] = a[i] - random.randint(1, 3)
                if a[i+1] <= 0: a[i+1] = 1
        else:
            a = [random.randint(self.a_min, self.a_max) for _ in range(n)]

        m = random.randint(self.m_min, self.m_max)
        operations = []
        expected_outputs = []
        current_a = a.copy()
        
        for _ in range(m):
            # 生成有效区间操作
            l = random.randint(1, n)
            r = random.randint(l, n)
            d = random.randint(self.d_min, self.d_max)
            operations.append({'l': l, 'r': r, 'd': d})
            
            # 更新当前数组状态
            for i in range(l-1, r):
                current_a[i] += d
                
            # 计算当前最大山脉宽度
            max_width = self.compute_max_hill_width(current_a)
            expected_outputs.append(max_width)

        return {
            'n': n,
            'a': a,
            'm': m,
            'operations': operations,
            'expected_outputs': expected_outputs
        }
    
    @staticmethod
    def prompt_func(question_case):
        # ...保持原有prompt结构，优化规则描述...
        return f"""Ealyonaandtowers's Towers Problem:
        
Input format:
n
a₁ a₂ ... aₙ
m
l₁ r₁ d₁
...
lₘ rₘ dₘ

After each operation, output the maximum hill width. A hill is a sequence of towers where:
1. There exists a peak position k
2. Towers strictly increase from left to the peak
3. Towers strictly decrease from the peak to right

Current Problem:
n = {question_case['n']}
Initial cubes: {' '.join(map(str, question_case['a']))}
m = {question_case['m']}
Operations:
{chr(10).join(f"{op['l']} {op['r']} {op['d']}" for op in question_case['operations'])}

Output the m results in order, each in [answer] tags:
[answer]
3
1
4
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_max_hill_width(arr):
        n = len(arr)
        max_width = 1  # 单个塔也算宽1的山脉
        left = [1] * n
        right = [1] * n

        # 预处理递增序列
        for i in range(1, n):
            if arr[i] > arr[i-1]:
                left[i] = left[i-1] + 1

        # 预处理递减序列
        for i in range(n-2, -1, -1):
            if arr[i] > arr[i+1]:
                right[i] = right[i+1] + 1

        # 计算最大宽度
        for i in range(n):
            current = left[i] + right[i] - 1
            if current > max_width:
                max_width = current

        return max_width
