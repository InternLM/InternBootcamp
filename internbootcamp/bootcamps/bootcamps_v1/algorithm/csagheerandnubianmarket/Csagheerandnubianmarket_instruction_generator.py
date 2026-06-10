import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answer(n, S, a):
    a_list = a.copy()
    def solve(k):
        if k == 0:
            return S  # 总成本0 <= S
        modified = [a_list[i] + (i + 1) * k for i in range(n)]
        modified_sorted = sorted(modified)
        sum_cost = sum(modified_sorted[:k])
        return S - sum_cost

    left = 0
    right = n + 1
    best_k = 0
    while left < right:
        mid = (left + right) // 2
        # 处理mid超出n的情况
        if mid > n:
            current = False
        else:
            res = solve(mid)
            current = res >= 0
        if current:
            best_k = mid
            left = mid + 1
        else:
            right = mid

    if best_k == 0:
        return (0, 0)
    else:
        modified = [a_list[i] + (i + 1) * best_k for i in range(n)]
        modified_sorted = sorted(modified)
        sum_cost = sum(modified_sorted[:best_k])
        return (best_k, sum_cost)


class CsagheerandnubianmarketInstructionGenerator(BaseInstructionGenerator):
    """Csagheerandnubianmarket Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, a_min=5, a_max=20, S_max=100):
        """
        初始化Csagheerandnubianmarket指令生成器
        
        Args:
            max_n: 参数描述
            a_min: 参数描述
            a_max: 参数描述
            S_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.a_min = a_min
        self.a_max = a_max
        self.S_max = S_max
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        a = [random.randint(self.a_min, self.a_max) for _ in range(n)]
        
        # 增加生成S极小值的概率
        if random.random() < 0.3:
            S = random.randint(0, 10)
        else:
            S = random.randint(0, self.S_max)
        
        k, T = compute_answer(n, S, a)
        return {
            'n': n,
            'S': S,
            'a': a,
            'correct_k': k,
            'correct_T': T
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        S_val = question_case['S']
        a_list = question_case['a']
        a_str = '、'.join(map(str, a_list))
        problem_text = f"""## 努比亚纪念品购买问题

你来到有特殊定价规则的努比亚市场。这里有{n}件商品（编号1~{n}），各商品基础价格分别为：{a_str} 埃及镑。

当购买k件商品时，选中第x件商品的实际成本为：基础价格 + 商品编号 × k。

你的预算是{S_val}埃及镑，需要**尽可能多买商品**。若存在多个方案，选择总成本最小的。

请计算最大可购买数量k及对应最小总成本T，按格式将答案放入[answer]标签。示例：
[answer]2 11[/answer]"""
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

