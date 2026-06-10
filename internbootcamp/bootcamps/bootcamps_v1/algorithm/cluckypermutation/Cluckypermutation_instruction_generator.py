import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from math import factorial
import random
import re




class CluckypermutationInstructionGenerator(BaseInstructionGenerator):
    """Cluckypermutation Bootcamp指令生成器"""
    
    def __init__(self, max_m=20):
        """
        初始化Cluckypermutation指令生成器
        
        Args:
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_m = max_m  # 控制最大排列长度防止阶乘溢出
    
    def case_generator(self):
        # 生成有效案例和无效案例的混合
        if random.random() < 0.5:
            # 有效案例：n >= m 且 k <= m!
            m = random.randint(1, min(12, self.max_m))  # 限制m保证阶乘计算不超限
            k = random.randint(1, factorial(m))
            n = random.randint(m, m + 100)
        else:
            # 无效案例：n < m 且 k > (m-1)! 
            m = random.randint(2, min(12, self.max_m))
            k = random.randint(factorial(m-1) + 1, factorial(m)*2)
            n = m - 1
        
        expected = self.calculate_answer(n, k)
        return {'n': n, 'k': k, 'expected': expected}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        return f"""给定整数n={n}和k={k}，请确定1~n的字典序第k个排列，并统计同时满足以下两个条件的位置数量：
1. 位置索引i是幸运数（由4/7组成的1-based索引）
2. 该位置的元素值a_i也是幸运数

如果第k个排列不存在，输出-1。最终答案放在[answer]标签内，例如：
[answer]0[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def calculate_answer(cls, n, k):
        # 验证排列是否存在
        m = 1
        while True:
            try:
                if factorial(m) >= k:
                    break
                m += 1
                if m > min(20, n+1):  # 防止无限循环
                    break
            except OverflowError:
                break
        if m > n:
            return -1

        # 生成排列后缀部分
        suffix = list(range(n-m+1, n+1))
        remaining_k = k
        for i in range(m):
            available = sorted(suffix[i:])
            slot_size = factorial(m - i - 1)

            # 计算当前块的位置
            pos = 0
            while remaining_k > slot_size:
                remaining_k -= slot_size
                pos += 1
                if pos >= len(available):
                    return -1  # 防止越界

            # 交换元素位置
            available[0], available[pos] = available[pos], available[0]
            # 保持后续元素有序
            suffix = suffix[:i] + available

        # 计算幸运数数量
        count = cls.count_lucky_numbers(n - m)

        # 检查后缀部分
        for idx, num in enumerate(suffix, start=n-m+1):
            if cls.is_lucky(idx) and cls.is_lucky(num):
                count += 1

        return count

    @staticmethod
    def is_lucky(x):
        return x > 0 and all(c in {'4', '7'} for c in str(x))

    @classmethod
    def count_lucky_numbers(cls, max_num):
        """使用BFS生成所有幸运数"""
        count = 0
        queue = ['4', '7']
        while queue:
            num = queue.pop(0)
            value = int(num)
            if value > max_num:
                continue
            count += 1
            queue.append(num + '4')
            queue.append(num + '7')
        return count
