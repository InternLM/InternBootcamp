import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CgukizhatesboxesInstructionGenerator(BaseInstructionGenerator):
    """Cgukizhatesboxes Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=10**3, max_a=10**4):
        """
        初始化Cgukizhatesboxes指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_a: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数调整支持更大规模的测试用例生成
        """
        self.max_n = max_n
        self.max_m = max_m
        self.max_a = max_a
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        a = [random.randint(0, self.max_a) for _ in range(n)]
        
        # 确保至少有一个非空堆的非零概率
        if sum(a) == 0:
            a[random.randint(0, n-1)] = random.randint(1, self.max_a)
        
        return {
            'n': n,
            'm': m,
            'a': a
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        a_str = ' '.join(map(str, question_case['a']))
        prompt = (
            "Professor GukiZ's students need to remove all boxes blocking his way. Here's the problem instance:\n\n"
            "Input Format:\n"
            "Two lines:\n"
            "1. Number of piles (n) and students (m)\n"
            "2. Space-separated list of boxes in each pile\n\n"
            "Problem Input:\n"
            f"{n} {m}\n"
            f"{a_str}\n\n"
            "Rules:\n"
            "1. Students start left of first pile and take 1 second to reach it\n"
            "2. Each subsequent operation (move or remove) takes 1 second\n"
            "3. Movement from pile i to i+1 requires pile i < n\n"
            "4. Remove operations can only happen on non-empty piles\n"
            "5. Students work simultaneously\n\n"
            "Output Requirement:\n"
            "The minimal time t in seconds to clear all boxes, put your final answer within [answer] and [/answer], e.g.:\n"
            "[answer]5[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_time(n, m, a):
        def check(t):
            remaining = list(a)
            idx = n - 1
            students = m

            while students > 0 and idx >= 0:
                if remaining[idx] == 0:
                    idx -= 1
                    continue

                required_time = idx + 1  # 移动到该堆需要的时间
                if t < required_time:
                    break

                working_time = t - required_time
                if working_time <= 0:
                    idx -= 1
                    continue

                students -= 1
                if working_time >= remaining[idx]:
                    working_time -= remaining[idx]
                    remaining[idx] = 0
                    idx -= 1

                    # 处理剩余时间
                    while working_time > 0 and idx >= 0:
                        if remaining[idx] == 0:
                            idx -= 1
                            continue
                        if working_time >= remaining[idx]:
                            working_time -= remaining[idx]
                            remaining[idx] = 0
                            idx -= 1
                        else:
                            remaining[idx] -= working_time
                            working_time = 0
                else:
                    remaining[idx] -= working_time

            return sum(remaining) == 0

        # 二分查找上下界优化
        left = 0
        right = sum(a) + n + 1  # 更精确的初始上界

        while left < right:
            mid = (left + right) // 2
            if check(mid):
                right = mid
            else:
                left = mid + 1

        return left
