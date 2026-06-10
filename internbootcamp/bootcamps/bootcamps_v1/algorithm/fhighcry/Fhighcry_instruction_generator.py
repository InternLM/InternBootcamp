import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class FhighcryInstructionGenerator(BaseInstructionGenerator):
    """Fhighcry Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=5, a_min=0, a_max=1e9):
        """
        初始化Fhighcry指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            a_min: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.a_min = a_min
        self.a_max = int(a_max)
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        if random.random() < 0.5:
            val = random.randint(self.a_min, self.a_max)
            heights = [val] * n
        else:
            heights = [random.randint(self.a_min, self.a_max) for _ in range(n)]
        
        return {
            'n': n,
            'heights': heights,
            'expected_answer': self._compute_answer(n, heights)
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        # 修正关键错误：从question_case中提取n和heights
        n = question_case['n']
        heights = question_case['heights']
        heights_str = ' '.join(map(str, heights))
        
        return f"""作为高喊山脊的声学研究员，你需要解决以下问题：

# 问题描述
给定{n}座连续排列的山峰，每座山峰的高度分别为：{heights_str}

请找出满足以下条件的不同山峰对(l, r)(1 ≤ l < r ≤ {n})的数量：
- 从第l座到第r座山峰（包含两端）所有山峰高度的按位或值
- 严格大于该区间内任意一座山峰的高度

# 输入格式
第一行：整数n (2 ≤ n ≤ 2e5)
第二行：n个整数表示山峰高度

# 输出格式
单个整数表示符合条件的对数

# 答案格式
请将最终答案放在[answer]和[/answer]标签之间，例如：[answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_answer(n, A):
        if n < 2: return 0

        # 原参考代码的实现保持不变
        L = [-1]*n
        stack = []
        for i in range(n):
            while stack and A[stack[-1]] < A[i]:
                stack.pop()
            L[i] = stack[-1] if stack else -1
            stack.append(i)

        R = [n]*n
        stack = []
        for i in reversed(range(n)):
            while stack and A[stack[-1]] <= A[i]:
                stack.pop()
            R[i] = stack[-1] if stack else n
            stack.append(i)

        L2 = [-1]*n
        last = [-1]*60
        for i in range(n):
            x = -1
            a = A[i]
            for j in range(60):
                if a & (1 << j):
                    last[j] = i
                else:
                    if last[j] > x:
                        x = last[j]
            L2[i] = max(L[i], x)

        R2 = [n]*n
        last = [n]*60
        for i in reversed(range(n)):
            x = n
            a = A[i]
            for j in range(60):
                if a & (1 << j):
                    last[j] = i
                else:
                    if last[j] < x:
                        x = last[j]
            R2[i] = min(R[i], x)

        ans = 0
        for i in range(n):
            ans += (L2[i]-L[i])*(R[i]-i) + (i-L[i])*(R[i]-R2[i]) - (L2[i]-L[i])*(R[i]-R2[i])
        return ans
