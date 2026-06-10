import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_min_balance_and_count(s):
    balance = 0
    min_balance = 0
    count = 0
    prefix = []
    for c in s:
        balance += 1 if c == '(' else -1
        prefix.append(balance)
        if balance < min_balance:
            min_balance = balance
            count = 1
        elif balance == min_balance:
            count += 1
    return min_balance, count, prefix

def calculate_real_beauty(s):
    total = sum(1 if c == '(' else -1 for c in s)
    if total != 0:
        return 0
    min_balance, count, prefix = compute_min_balance_and_count(s)
    overall_min = min(prefix)
    if overall_min < 0:
        return 0
    return count

def optimal_solution(n, s):
    max_beauty = 0
    best_pair = (1, 1)
    original_beauty = calculate_real_beauty(s)
    max_beauty = original_beauty
    
    s_list = list(s)
    for i in range(n):
        for j in range(i, n):
            if s_list[i] == s_list[j]:
                continue
            
            # Perform swap
            s_list[i], s_list[j] = s_list[j], s_list[i]
            new_s = ''.join(s_list)
            current_beauty = calculate_real_beauty(new_s)
            
            if current_beauty > max_beauty:
                max_beauty = current_beauty
                best_pair = (i+1, j+1)
            
            # Revert swap
            s_list[i], s_list[j] = s_list[j], s_list[i]
    
    return (max_beauty, best_pair[0], best_pair[1])


class BtheworldisjustaprogrammingtaskhardversionInstructionGenerator(BaseInstructionGenerator):
    """Btheworldisjustaprogrammingtaskhardversion Bootcamp指令生成器"""
    
    def __init__(self, max_n=12):
        """
        初始化Btheworldisjustaprogrammingtaskhardversion指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n  # 控制案例规模保证验证效率
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        # 生成有效测试案例（包含平衡和非平衡情况）
        if random.random() < 0.5 and n % 2 == 0:
            # 生成平衡括号字符串
            s = ['(']*(n//2) + [')']*(n//2)
            random.shuffle(s)
            s = ''.join(s)
        else:
            # 随机生成可能不平衡的字符串
            s = ''.join(random.choices(['(', ')'], k=n))
        
        max_beauty, l, r = optimal_solution(n, s)
        return {
            'n': n,
            's': s,
            'expected_max': max_beauty,
            'swap_l': l,
            'swap_r': r
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        s = question_case['s']
        return f"""给定一个长度为{n}的括号字符串："{s}"
请通过交换两个字符（允许相同位置），最大化循环移位构成有效括号序列的数量。输出最大数量及交换位置（1-based）。

有效括号序列定义：
1. 空字符串
2. (A) 其中A是有效序列
3. AB 其中A和B都是有效序列

答案格式：
[answer]
{{最大数量}}
{{位置1}} {{位置2}}
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

