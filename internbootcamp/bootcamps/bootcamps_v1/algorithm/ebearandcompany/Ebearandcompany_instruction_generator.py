import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
from collections import defaultdict
import re

# === 源文件中的全局函数 ===

def compute_min_swaps(n, s):
    a, b, c = [], [], []
    for i in range(n):
        char = s[i]
        if char == 'V':
            a.append(i)
        elif char == 'K':
            b.append(i)
        else:
            c.append(i)
    
    def count(arr, st, x):
        ret = 0
        i = st
        while i < len(arr) and arr[i] < x:
            ret += 1
            i += 1
        return ret
    
    dp = defaultdict(lambda: float('inf'))
    dp[(0, 0, 0, 0)] = 0
    
    for i in range(len(a)+1):
        for j in range(len(b)+1):
            for k in range(len(c)+1):
                for p in range(2):
                    current_key = (i, j, k, p)
                    current_val = dp[current_key]
                    if current_val == float('inf'):
                        continue
                    
                    # Place V
                    if i < len(a):
                        cost = count(a, i, a[i]) + count(b, j, a[i]) + count(c, k, a[i])
                        new_key = (i+1, j, k, 1)
                        dp[new_key] = min(dp[new_key], current_val + cost)
                    
                    # Place K (only if previous was not V)
                    if j < len(b) and p == 0:
                        cost = count(a, i, b[j]) + count(b, j, b[j]) + count(c, k, b[j])
                        new_key = (i, j+1, k, 0)
                        dp[new_key] = min(dp[new_key], current_val + cost)
                    
                    # Place other characters
                    if k < len(c):
                        cost = count(a, i, c[k]) + count(b, j, c[k]) + count(c, k, c[k])
                        new_key = (i, j, k+1, 0)
                        dp[new_key] = min(dp[new_key], current_val + cost)
    
    return min(dp[(len(a), len(b), len(c), 0)], dp[(len(a), len(b), len(c), 1)])


class EbearandcompanyInstructionGenerator(BaseInstructionGenerator):
    """Ebearandcompany Bootcamp指令生成器"""
    
    def __init__(self, min_length=1, max_length=75):
        """
        初始化Ebearandcompany指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_length = min_length
        self.max_length = max_length
    
    def case_generator(self):
        # 保证至少有一定概率生成包含VK的情况
        n = random.randint(self.min_length, self.max_length)
        # 提高生成包含V和K的概率
        population = list(string.ascii_uppercase) + ['V', 'K']*3
        s = ''.join(random.choices(population, k=n))
        correct_answer = compute_min_swaps(n, s)
        return {
            'n': n,
            's': s,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""Bear Limak需要修改字符串以避免出现"VK"子串。每次只能交换相邻字符，求最少交换次数。

输入格式：
第一行：整数n（1 ≤ n ≤ 75）
第二行：由大写字母组成的字符串

当前问题：
{question_case['n']}
{question_case['s']}

请计算最小交换次数，并将整数答案包裹在[answer]和[/answer]标签中。例如：[answer]3[/answer]

注意：
1. 必须读取两行标准输入
2. 最终答案必须是整数形式""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

