import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answer(n, s):
    if '1' not in s:  # 快速返回全0情况
        return 0
    
    r = [0] * n
    g = [[] for _ in range(n + 2)]
    a = [0] * n
    i = n - 1
    while i >= 0:
        if s[i] == '1':
            j = i
            while j >= 0 and s[j] == '1':
                r[j] = i + 1
                j -= 1
            while i > j:
                x = i - j
                if g[x+1]:
                    a[i] = x * (g[x+1][-1] - i) + a[g[x+1][-1]]
                else:
                    a[i] = x * (n - i)
                g[x].append(i)
                i -= 1
        else:
            i -= 1
    ans = 0
    c = 0
    for i in range(n):
        c += 1
        if s[i] == '0':
            continue
        t = r[i]
        b = t - i
        if i == 0 or s[i-1] == '0':
            for j in range(1, b+1):
                if g[j]:
                    g[j].pop()
        u = b * (b + 1) // 2
        if g[b+1]:
            x = g[b+1][-1]
            u += (x - t) * b + a[x]
        else:
            u += (n - t) * b
        ans += c * u
        c = 0
    return ans


class FfruitsequencesInstructionGenerator(BaseInstructionGenerator):
    """Ffruitsequences Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=12, p_1=0.5, edge_case_prob=0.2):
        """
        初始化Ffruitsequences指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            p_1: 参数描述
            edge_case_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(1, n_min)
        self.n_max = max(self.n_min, n_max)
        self.p_1 = max(0.0, min(1.0, p_1))
        self.edge_case_prob = max(0.0, min(1.0, edge_case_prob))
    
    def case_generator(self):
        # 生成策略优化
        if random.random() < self.edge_case_prob:
            n = random.randint(self.n_min, self.n_max)
            choice = random.choice(['all_zero', 'all_one', 'alternating'])
            if choice == 'all_zero':
                s = '0' * n
            elif choice == 'all_one':
                s = '1' * n
            else:  # 010101...模式
                s = ''.join(['01'[i%2] for i in range(n)])
        else:
            n = random.randint(self.n_min, self.n_max)
            s = ''.join(random.choices(['0','1'], 
                         weights=[1-self.p_1, self.p_1], k=n))
        
        return {
            'n': n,
            's': s,
            'correct_answer': compute_answer(n, s)
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        s = question_case['s']
        return f"""根据以下条件计算所有子串的最长连续1长度之和：

输入格式：
n = {n}
s = {s}

计算要求：
1. 遍历所有可能的子串s[l..r] (1 ≤ l ≤ r ≤ n)
2. 对每个子串找出最长连续的1的个数
3. 求所有子串的对应数值之和

请将最终答案用[answer]标签包裹，例如：[answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

