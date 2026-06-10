import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import Counter




class DchangingarrayInstructionGenerator(BaseInstructionGenerator):
    """Dchangingarray Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=10, k_min=1, k_max=5):
        """
        初始化Dchangingarray指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            k_min: 参数描述
            k_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min  # 允许生成n=1的边界情况
        self.n_max = n_max
        self.k_min = k_min
        self.k_max = k_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        k = random.randint(self.k_min, self.k_max)
        max_val = (1 << k) - 1
        
        # 允许生成全零数组
        a = [random.randint(0, max_val) for _ in range(n)]
        return {'n': n, 'k': k, 'a': a}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        k = question_case['k']
        a = ' '.join(map(str, question_case['a']))
        return f"""## 异或子数组最大值问题

**问题描述**
给定一个包含{n}个{k}位整数的数组，每个元素可以被替换为它的补码（所有二进制位取反）。请找出通过任意次数的操作后，可以得到的最多非零异或连续子数组的数量。

**输入格式**
第一行：n k
第二行：a_1 a_2 ... a_n

**当前测试案例**
{n} {k}
{a}

**输出要求**
将最终答案放在[answer]和[/answer]标签之间，例如：[answer]42[/answer]

**注意**
1. 补码定义：k位整数的补码是所有位取反后的结果
2. 子数组的异或值为所有元素按位异或的结果
3. 需要最大化满足异或值非零的子数组数量""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve(n, k, a):
        def flip(x):
            return (1 << k) - 1 - x

        prefix = [0]
        for num in a:
            prefix.append(prefix[-1] ^ num)

        cnt = Counter(prefix)
        total = n * (n + 1) // 2
        processed = set()

        for key in cnt:
            if key in processed:
                continue

            complement = flip(key)
            # 处理键对避免重复计算
            if key > complement and complement in cnt:
                processed.update([key, complement])
                continue

            # 计算当前键和补码的总出现次数
            current_count = cnt[key]
            complement_count = cnt.get(complement, 0) if key != complement else 0

            # 合并相同补码的情况
            total_pairs = current_count + complement_count if key != complement else current_count

            # 最优分割策略
            max_half = (total_pairs + 1) // 2
            min_half = total_pairs // 2
            total -= max_half * (max_half - 1) // 2
            total -= min_half * (min_half - 1) // 2

            processed.update({key, complement})

        return total
