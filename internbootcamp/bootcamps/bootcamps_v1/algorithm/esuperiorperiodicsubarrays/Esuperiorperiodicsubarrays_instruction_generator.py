import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
from collections import defaultdict
import random
import re

# === 源文件中的全局函数 ===

def solve_puzzle(n, a):
    if n == 1:
        return 0  # s必须≥1且<1，无解

    a_extended = a.copy()
    a_extended.extend(a)
    inf = min(a) - 1
    a_extended[-1] = inf  # 保证最后元素最小
    result = 0

    numbers_by_gcd = defaultdict(list)
    for i in range(1, n):
        current_gcd = math.gcd(i, n)
        numbers_by_gcd[current_gcd].append(i)

    for d in numbers_by_gcd:  # 遍历每个可能的gcd值
        if n % d != 0:
            continue
        
        # 计算每个模位的最大值
        m = [-math.inf] * d
        for i in range(n):
            mod = i % d
            if a_extended[i] > m[mod]:
                m[mod] = a_extended[i]
        
        l = 0
        r = 0
        max_r = len(a_extended) - 1  # 防止越界
        while l < n and r <= max_r:
            if a_extended[r] < m[r % d]:
                # 处理当前有效区间
                sorted_s = sorted(numbers_by_gcd[d])
                for s in sorted_s:
                    if s > (r - l):
                        break
                    # 计算有效区间长度
                    start = l
                    end = min(r - s, n - 1)
                    if start <= end:
                        result += end - start + 1
                l = r + 1
                r = l
            else:
                r += 1
    return result


class EsuperiorperiodicsubarraysInstructionGenerator(BaseInstructionGenerator):
    """Esuperiorperiodicsubarrays Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, max_a=10):
        """
        初始化Esuperiorperiodicsubarrays指令生成器
        
        Args:
            max_n: 参数描述
            max_a: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max(max_n, 1)  # 保证n≥1
        self.max_a = max_a
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        a = [random.randint(1, self.max_a) for _ in range(n)]
        return {
            'n': n,
            'a': a,
            'correct_answer': solve_puzzle(n, a)
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a_str = ' '.join(map(str, question_case['a']))
        if n == 1:
            s_range_hint = "（注意：当n=1时没有有效的s值）"
        else:
            s_range_hint = f"其中1 ≤ s < {n}"
        
        return f"""请解决以下无限周期数组问题：

给定参数：
- 原始数组长度n = {n}
- 数组元素 = [{a_str}]

需要找出所有满足以下条件的(l, s)对：
1. 起始位置l满足0 ≤ l < {n}
2. 周期长度s满足{s_range_hint}
3. 对于所有k ≥ 0，子数组在位置k的元素 ≥ 原数组位置k的元素

规则详解：
- 子数组定义为从l开始取s个元素，并无限重复：元素k的值为a[(l + k) % {n}]
- 比较时，原数组元素k的值为a[k % {n}]

输出要求：
- 输出最终答案的整数形式
- 将答案放在[answer]标签内，如：[answer]0[/answer]

请计算符合条件的总对数：""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

