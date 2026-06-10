import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict
import bisect

# === 源文件中的全局函数 ===

def compute_possible_m(a):
    cnt1 = a.count(1)
    n = len(a)
    a_sorted = sorted(a)
    freq = defaultdict(int)
    for num in a_sorted:
        freq[num] += 1

    def is_possible(m):
        current_freq = freq.copy()

        if current_freq.get(1, 0) < m:
            return False
        current_freq[1] -= m

        last = [1] * m
        current_power = 2
        cnt = m

        while current_freq.get(current_power, 0) > 0 and cnt > 0:
            available = current_freq[current_power]
            take = min(available, cnt)
            current_freq[current_power] -= take
            for i in range(take):
                last[i] = current_power
            cnt = take
            current_power *= 2

        last_sorted = sorted(last)
        remaining = []
        for num, count in sorted(current_freq.items()):
            if count > 0:
                remaining.extend([num] * count)

        for num in remaining:
            required = (num + 1) // 2
            idx = bisect.bisect_left(last_sorted, required)
            if idx >= len(last_sorted):
                return False
            del last_sorted[idx]
            bisect.insort(last_sorted, num)

        return True

    left, right = 0, cnt1 + 1
    while left < right - 1:
        mid = (left + right) // 2
        if is_possible(mid):
            right = mid
        else:
            left = mid
    mi = right

    if mi > cnt1:
        return [-1]
    return list(range(mi, cnt1 + 1))


class EprairiepartitionInstructionGenerator(BaseInstructionGenerator):
    """Eprairiepartition Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Eprairiepartition指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params
        self.min_m = params.get('min_m', 1)
        self.max_m = params.get('max_m', 3)
        self.invalid_prob = params.get('invalid_prob', 0.3)
    
    def case_generator(self):
        if random.random() < self.invalid_prob:
            # Generate invalid case
            invalid_cases = [
                [1, 2, 4, 4, 4],
                [3, 3, 3],
                [5, 5],
                [2, 3, 3]
            ]
            a = random.choice(invalid_cases)
            a.sort()
        else:
            # Generate valid case
            m0 = random.randint(self.min_m, self.max_m)
            summands_list = []
            for _ in range(m0):
                k = random.randint(0, 3)
                sum_part = (2 ** k) - 1 if k > 0 else 0
                max_r = 2 ** k if k > 0 else 1
                r = random.randint(1, max_r)
                summands = [2 ** i for i in range(k)] + [r]
                summands_list.extend(summands)
            a = sorted(summands_list)
        
        possible_m = compute_possible_m(a)
        return {
            'n': len(a),
            'a': a,
            'correct_output': possible_m
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        a_str = ' '.join(map(str, a))
        prompt = f"""你是一个数学问题的解答者。根据以下描述解决该问题。

题目背景：

每个正整数x可以唯一表示为x = 1 + 2 + 4 + ... + 2^(k-1) + r的形式，其中k是非负整数，0 < r ≤ 2^k。这称为x的草原划分。例如，7的草原划分为1+2+4，12的草原划分为1+2+4+5。

Alice将原数列中的每个元素替换为其草原划分的所有加数，然后将所有加数按非降序排列得到一个序列。现在给定这个序列，需要找出所有可能的原数列的长度m的可能值。

输入格式：

第一行是一个整数n，表示序列的长度。
第二行有n个按非降序排列的整数a_1, a_2, ..., a_n。

输出格式：

输出所有可能的m的非降序排列，每个值之间用空格隔开。如果没有可能的m，输出-1。

现在，给定以下具体输入：

n = {n}
序列为：{a_str}

请仔细分析问题，确定所有可能的m的值。将你的答案放入[answer]和[/answer]的标签中。例如，若答案是2和3，则写成[answer]2 3[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

