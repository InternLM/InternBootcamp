import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DtooeasyproblemsInstructionGenerator(BaseInstructionGenerator):
    """Dtooeasyproblems Bootcamp指令生成器"""
    
    def __init__(self, n=5, ti_min=1, ti_max=100):
        """
        初始化Dtooeasyproblems指令生成器
        
        Args:
            n: 参数描述
            ti_min: 参数描述
            ti_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.ti_min = ti_min
        self.ti_max = ti_max
    
    def case_generator(self):
        """生成保证有解的谜题实例"""
        n = self.n
        if n == 0:  # 处理边界情况
            return {'n': 0, 'T': 0, 'problems': []}
        
        # 确定最大可能的k值
        k = random.randint(1, n)
        
        # 生成k个有效问题
        valid = []
        total_time = 0
        for _ in range(k):
            a = random.randint(k, n)  # 保证a_i >= k
            t = random.randint(self.ti_min, self.ti_max)
            valid.append((a, t))
            total_time += t
        
        # 生成无效问题（a_i <k 或时间过大）
        invalid = []
        for _ in range(n - k):
            a = random.randint(1, k-1) if k > 1 else 1  # 确保a_i <k
            t = random.randint(total_time+1, total_time*2)  # 时间无法被选中
            invalid.append((a, t))
        
        # 合并并打乱问题顺序
        all_problems = valid + invalid
        random.shuffle(all_problems)
        
        return {
            'n': n,
            'T': total_time,
            'problems': all_problems
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """生成符合格式的问题描述"""
        problem_lines = "\n".join(
            f"{i+1} {a} {t}" 
            for i, (a, t) in enumerate(question_case['problems'])
        )
        return f"""You are preparing for a scheduling theory exam lasting {question_case['T']}ms with {question_case['n']} problems. Solve problems to maximize your score. Each problem i gives a point only if solved ≤a_i total problems.

Input:
{question_case['n']} {question_case['T']}
{problem_lines}

Output your answer as:

[answer]
s
k
p1 p2 ... pk
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve_problem(n, T, problems):
        """参考解法（带索引处理）"""
        indexed_problems = [(i+1, a, t) for i, (a, t) in enumerate(problems)]
        # 按ti升序，a降序排序（优先选择耗时少且a高的）
        sorted_problems = sorted(indexed_problems, key=lambda x: (x[2], -x[1]))

        # 二分查找最大k
        low, high = 0, n
        best_k = 0
        while low <= high:
            mid = (low + high) // 2
            cnt, total = 0, 0
            for p in sorted_problems:
                if p[1] >= mid and total + p[2] <= T:
                    cnt += 1
                    total += p[2]
                if cnt >= mid:
                    break
            if cnt >= mid:
                best_k = mid
                low = mid + 1
            else:
                high = mid - 1

        # 收集答案索引
        result = []
        total = 0
        for p in sorted_problems:
            if p[1] >= best_k and total + p[2] <= T and len(result) < best_k:
                result.append(p[0])
                total += p[2]

        return {
            's': best_k,
            'k': best_k,
            'p_list': result
        }
