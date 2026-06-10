import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from functools import reduce
from operator import mul




class CrandomeventsInstructionGenerator(BaseInstructionGenerator):
    """Crandomevents Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=5, **params):
        """
        初始化Crandomevents指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = min(max_n, 100000)
        self.max_m = min(max_m, 100000)
        self.params = params
    
    def case_generator(self):
        # 控制案例类型分布
        case_type = random.choice(['sorted', 'unsorted', 'boundary'])
        
        # 生成基本参数
        n = random.randint(1, self.max_n)
        m = random.randint(0, self.max_m)
        
        # 生成排列逻辑
        if case_type == 'sorted':
            a = list(range(1, n+1))
        else:
            sorted_arr = list(range(1, n+1))
            # 生成最大正确后缀长度
            k = 0
            if n > 0:
                k = random.randint(0, n)
            a = sorted_arr.copy()
            if k < n:
                # 搅乱前 n-k 个元素
                prefix = a[:n-k]
                random.shuffle(prefix)
                a = prefix + a[n-k:]
        
        # 实际检查排序状态
        is_sorted = a == sorted(a)
        
        # 生成实验数据
        experiments = []
        applicable_probs = []
        
        # 计算实际有效后缀长度
        last_wrong = n
        for i in reversed(range(n)):
            if a[i] != i+1:
                last_wrong = i
                break
        
        for _ in range(m):
            # 智能生成有效的r值
            if random.random() < 0.7 and last_wrong < n:
                r = random.randint(last_wrong+1, n)
            else:
                r = random.randint(1, n)
            p = round(random.uniform(0, 1), 6)
            experiments.append((r, p))
            
            # 判断该实验是否可能影响最终结果
            if r > last_wrong:
                applicable_probs.append(1 - p)

        # 计算正确概率
        if m == 0:
            prob = 1.0 if is_sorted else 0.0
        else:
            if is_sorted:
                prob = 1.0
            else:
                try:
                    total_prob = 1.0 - reduce(mul, applicable_probs, 1.0)
                except:
                    total_prob = 0.0
                # 四舍五入处理
                prob = round(total_prob, 6)
                prob = max(0.0, min(1.0, prob))

        return {
            'n': n,
            'm': m,
            'a': a,
            'experiments': experiments,
            'correct_answer': prob
        }
    
    @staticmethod
    def prompt_func(question_case):
        exp_list = "\n".join(
            f"{r} {p:.6f}" 
            for r, p in question_case['experiments']
        )
        return f"""## Permutation Probability Problem

Given a permutation of {question_case['n']} numbers: {' '.join(map(str, question_case['a']))}
After applying {question_case['m']} experiments in order:

{exp_list}

Calculate the final probability that the permutation becomes fully sorted.

Output Requirements:
1. Answer must contain exactly 6 decimal places
2. Format as [answer]<result>[/answer]
3. Use standard decimal notation (no scientific notation)

Example:
[answer]0.123456[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

