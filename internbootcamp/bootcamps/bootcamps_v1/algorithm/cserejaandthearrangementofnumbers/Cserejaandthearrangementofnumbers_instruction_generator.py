import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CserejaandthearrangementofnumbersInstructionGenerator(BaseInstructionGenerator):
    """Cserejaandthearrangementofnumbers Bootcamp指令生成器"""
    
    def __init__(self, max_n=2000000, max_m=100000, default_n=100, default_m=10):
        """
        初始化Cserejaandthearrangementofnumbers指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            default_n: 参数描述
            default_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
        self.default_n = default_n
        self.default_m = default_m
    
    def case_generator(self):
        n = random.randint(1, self.default_n)
        m = random.randint(1, self.default_m)
        q_list = []
        while len(q_list) < m:
            q = random.randint(1, 10**5)
            if q not in q_list:
                q_list.append(q)
        w_list = [random.randint(1, 10**5) for _ in range(m)]
        
        k = 0
        while True:
            k_candidate = k + 1
            if k_candidate % 2 == 1:
                l = (k_candidate * (k_candidate - 1)) // 2 + 1
            else:
                l = (k_candidate ** 2) // 2
            if l > n:
                break
            k = k_candidate
        w_sorted = sorted(w_list, reverse=True)
        if k <= m:
            correct_sum = sum(w_sorted[:k])
        else:
            correct_sum = sum(w_sorted)
        coupons = list(zip(q_list, w_list))
        return {
            'n': n,
            'm': m,
            'coupons': coupons,
            'correct_sum': correct_sum
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        coupons = question_case['coupons']
        lines = [f"{n} {m}"]
        for q, w in coupons:
            lines.append(f"{q} {w}")
        problem_instance = "\n".join(lines)
        prompt = f"""问题描述：

定义一个由n个整数组成的数组为“美丽数组”，当且仅当满足以下条件：

考虑数组中的所有不同的数对x和y（x≠y），其中x和y都出现在数组中。对于每一对x和y，必须存在至少一个位置j（1 ≤j <n），使得aj=x且aj+1=y，或者aj=y且aj+1=x。

Dima会构造这样的美丽数组a，包含n个元素。Sereja需要支付的金额等于数组中所有不同qi对应的wi的总和。你的任务是计算Sereja可能支付的最大金额。

输入格式：
第一行是两个整数n和m，分别表示数组的长度和优惠券的数量。
接下来m行，每行两个整数qi和wi，表示每个优惠券允许使用的数字和对应的费用。

输出格式：
输出一个整数，表示Sereja可能支付的最大金额。

请根据以下输入数据求解问题：

{problem_instance}

请将最终答案放入[answer]标签中，例如：[answer]12345[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

