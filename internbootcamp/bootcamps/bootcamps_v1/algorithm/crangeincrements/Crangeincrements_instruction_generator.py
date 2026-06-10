import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def solve(a_list):
    n = len(a_list)
    l = a_list.copy()
    ans = []
    s = []
    opened = []
    for i in range(n):
        current = l[i]
        if not s or current > s[-1]:
            s.append(current)
            opened.append(i + 1)
        elif current < s[-1]:
            while s and current < s[-1]:
                pp = True
                base = current
                if len(s) > 1:
                    base = max(base, s[-2])
                if base == current:
                    pp = False
                val = s[-1] - base
                while val > 0:
                    ans.append(f"{opened[-1]} {i}")
                    val -= 1
                if pp:
                    s.pop()
                    opened.pop()
                else:
                    break
            if s:
                s[-1] = current
    while s:
        base = 0
        if len(s) > 1:
            base = s[-2]
        val = s[-1] - base
        while val > 0:
            ans.append(f"{opened[-1]} {n}")
            val -= 1
        s.pop()
        opened.pop()
    operations = []
    for op in ans:
        li, ri = map(int, op.split())
        operations.append((li, ri))
    return operations


class CrangeincrementsInstructionGenerator(BaseInstructionGenerator):
    """Crangeincrements Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10, max_val=5):
        """
        初始化Crangeincrements指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.max_val = max_val
    
    def case_generator(self):
        while True:
            n = random.randint(self.min_n, self.max_n)
            a = [random.randint(0, self.max_val) for _ in range(n)]
            if sum(a) == 0:  # 确保至少一个正元素
                continue
            try:
                correct_ops = solve(a)
            except:
                continue  # 防止极端情况异常
            if len(correct_ops) > 1e5:  # 题目保证答案次数不超过1e5
                continue
            return {
                'n': n,
                'a': a,
                'correct_t': len(correct_ops),
                'correct_ops': correct_ops
            }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = ' '.join(map(str, question_case['a']))
        prompt = f"""Polycarpus需要确定最少的函数调用次数，使得初始全为0的数组变成给定的状态。函数rangeIncrement(l, r)每次将下标l到r的元素加1。你需要解决这个问题。

输入格式：
第一行是整数n，表示数组长度。
第二行是n个整数，表示数组的最终状态。

当前的问题实例：
输入的第一行：{n}
输入的第二行：{a}

请你输出最少的调用次数t，并给出每次调用的l和r参数。可能有多个正确答案，只要满足次数最少即可。

请将答案按照以下格式输出，答案必须包含在[answer]和[/answer]之间：

[answer]
t
l1 r1
l2 r2
...
lt rt
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

