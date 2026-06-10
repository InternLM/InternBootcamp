import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局函数 ===

def compute_expected(n, a_str, b_str):
    a = [[[] for _ in range(26)] for __ in range(2)]
    for i, s in enumerate([a_str, b_str]):
        for j, c in enumerate(s):
            idx = ord(c) - ord('A')
            a[i][idx].append(j)
    
    total = 0
    for char_idx in range(26):
        p = a[0][char_idx]
        q = a[1][char_idx]
        if not p or not q:
            continue
        
        q_sum = sum(q)
        p_len = len(p)
        q_len = len(q)
        j = 0
        t = 0
        
        for x in p:
            # 维护双指针找到q中第一个不小于x的位置
            while j < q_len and q[j] < x:
                t += q[j]
                j += 1
            
            # 计算两项贡献（参考原算法逻辑）
            part1 = (t + j * x) * (n - x)
            part2 = (x + 1) * (n * (q_len - j) - (q_sum - t))
            total += part1 + part2
    
    # 计算分母：n*(n+1)*(2n+1)/6
    denominator = n * (n + 1) * (2 * n + 1) / 6
    if denominator == 0:
        return 0.0
    return total * 6.0 / (n * (n + 1) * (2 * n + 1))


class ClittleelephantandfurikandrubikInstructionGenerator(BaseInstructionGenerator):
    """Clittleelephantandfurikandrubik Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=200000):
        """
        初始化Clittleelephantandfurikandrubik指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(self.min_n, min(self.max_n, 10))  # 默认测试限制n<=10
        a = ''.join(random.choices(string.ascii_uppercase, k=n))
        b = ''.join(random.choices(string.ascii_uppercase, k=n))
        expected = compute_expected(n, a, b)
        return {
            "n": n,
            "a": a,
            "b": b,
            "expected": expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        b = question_case['b']
        prompt = f"""你是数学竞赛选手，请解决以下期望值计算问题：

给定两个长度均为{n}的字符串：
字符串a：{a}
字符串b：{b}

定义所有有效子串对(x,y)为从a和b中分别选取的等长子串。求在所有可能子串对中，x与y在相同位置上字符相等的数量的数学期望。

请先分析问题，给出计算步骤，最后将答案（保留9位小数）放入[answer]标签内。例如：[answer]0.400000000[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

