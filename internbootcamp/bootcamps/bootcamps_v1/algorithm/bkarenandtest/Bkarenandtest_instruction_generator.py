import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, a_list):
    mod = MOD
    a = list(a_list)
    sgn = 1
    current_n = n
    
    while current_n % 4 != 1:
        current_n -= 1
        b = []
        current_sgn = sgn
        for i in range(current_n):
            val = (a[i] + current_sgn * a[i+1]) % mod
            b.append(val)
            current_sgn *= -1
        a = b
        sgn *= -1  # Update the starting sign for the next layer
    
    m = current_n // 2
    max_inv = m if m > 1 else 2
    inv = [0] * (max_inv + 2)
    inv[0] = inv[1] = 1
    for i in range(2, m + 1):
        inv[i] = (mod - mod // i * inv[mod % i]) % mod
    
    p = [0] * current_n
    r = p[0] = 1
    for i in range(m):
        coeff = (m - i) * inv[i + 1] % mod
        r = r * coeff % mod
        p[2 * i + 2] = r
    
    ans = 0
    for i in range(current_n):
        ans = (ans + a[i] * p[i]) % mod
    
    return ans % mod


class BkarenandtestInstructionGenerator(BaseInstructionGenerator):
    """Bkarenandtest Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=5, min_val=1, max_val=10**9, **kwargs):
        """
        初始化Bkarenandtest指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_val: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.min_n = min_n
        self.max_n = max_n
        self.min_val = min_val
        self.max_val = max_val
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        a = [random.randint(self.min_val, self.max_val) for _ in range(n)]
        answer = compute_answer(n, a)
        return {
            'n': n,
            'a': a,
            'answer': answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        a = ' '.join(map(str, question_case['a']))
        return f"""Karen有一道特殊的数学测试题。题目规则如下：

1. 初始有n个整数，按顺序排列成一行
2. 每步生成新行：交替对相邻数进行加减操作
   - 第一行起始操作为加法，后续每行起始操作与上行的最后操作相反
   - 重复该过程直到只剩一个数
3. 最终结果需对{ MOD }取模，输出非负余数

输入数据：
- 第一行是整数n（当前n={n}）
- 第二行包含{n}个整数：{a}

请逐步思考并计算最终结果，将答案用[answer]标签包裹，例如：[answer]42[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

