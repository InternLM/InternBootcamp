import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def calculate_min_prefix_sums(arr):
    n = len(arr)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i+1] = prefix[i] + arr[i]
    
    min_sums = [float('inf')] * (n + 1)
    for k in range(1, n+1):
        min_sum = min(prefix[i+k] - prefix[i] for i in range(n - k + 1))
        min_sums[k] = min_sum
    return min_sums

def calculate_max_area(n, m, a, b, x):
    min_a = calculate_min_prefix_sums(a)
    min_b = calculate_min_prefix_sums(b)
    
    max_area = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            if min_a[i] * min_b[j] <= x:
                max_area = max(max_area, i * j)
    return max_area


class CmaximumsubrectangleInstructionGenerator(BaseInstructionGenerator):
    """Cmaximumsubrectangle Bootcamp指令生成器"""
    
    def __init__(self, max_n=2000, max_m=2000, max_val=2000):
        """
        初始化Cmaximumsubrectangle指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数说明:
            max_n: a数组的最大长度（符合题目约束）
            max_m: b数组的最大长度（符合题目约束）
            max_val: 数组元素的最大值（符合题目约束）
        """
        super().__init__()
        self.max_n = max_n
        self.max_m = max_m
        self.max_val = max_val
    
    def case_generator(self):
        # 生成随机长度（1 ≤ n, m ≤ 2000）
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        
        # 生成随机数组（元素范围1~2000）
        a = [random.randint(1, self.max_val) for _ in range(n)]
        b = [random.randint(1, self.max_val) for _ in range(m)]
        
        # 计算最小子数组和
        min_a = calculate_min_prefix_sums(a)
        min_b = calculate_min_prefix_sums(b)
        
        # 收集所有可能的乘积
        products = []
        for i in range(1, n+1):
            for j in range(1, m+1):
                products.append(min_a[i] * min_b[j])
        
        # 生成x的策略（确保覆盖所有边界情况）
        if not products:  # 理论上不可能发生
            x = 1
        else:
            min_product = min(products)
            max_product = max(products)
            
            # 生成模式选择（按概率分布）
            mode = random.choices(
                population=[0, 1, 2, 3],
                weights=[0.3, 0.3, 0.2, 0.2],  # 增加无解情况的概率
                k=1
            )[0]
            
            if mode == 0:   # 正常范围解
                x = random.randint(min_product, max_product)
            elif mode == 1: # 无解情况
                x = random.randint(1, min_product-1) if min_product > 1 else 0
            elif mode == 2: # 超大值覆盖所有解
                x = max_product * random.randint(1, 100)
            else:          # 极小值特殊情况
                x = 1 if random.random() < 0.5 else 0
        
        # 确保x符合题目约束（1 ≤ x ≤ 2e9）
        x = max(1, min(x, 2*10**9))
        
        return {
            'n': n,
            'm': m,
            'a': a.copy(),
            'b': b.copy(),
            'x': x
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""给定两个正整数数组：
数组a（长度={question_case['n']}）：{question_case['a']}
数组b（长度={question_case['m']}）：{question_case['b']}

定义矩阵c，其中每个元素c[i][j] = a[i] × b[j]。请找到c中元素和不超过{question_case['x']}的最大矩形区域（元素个数最多）。如果不存在这样的区域，输出0。

答案必须为整数且用[ANSWER]标签包裹，例如：[ANSWER]0[/ANSWER] 或 [ANSWER]42[/ANSWER]
""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

