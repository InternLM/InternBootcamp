import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class DrearrangeInstructionGenerator(BaseInstructionGenerator):
    """Drearrange Bootcamp指令生成器"""
    
    def __init__(self, n=3, m=3):
        """
        初始化Drearrange指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.m = m
    
    def case_generator(self):
        """
        生成保证存在解的原矩阵案例
        """
        while True:
            # 生成随机矩阵并确保存在解
            n, m = self.n, self.m
            total = n * m
            elements = list(range(1, total + 1))
            random.shuffle(elements)
            original = [elements[i*m:(i+1)*m] for i in range(n)]
            
            # 尝试生成解矩阵
            solution = self._generate_solution(original)
            if solution is not None:
                # 提取原矩阵的X和Y
                X = list({max(row) for row in original})
                Y = list({max(col) for col in zip(*original)})
                return {
                    'n': n, 
                    'm': m, 
                    'matrix': original, 
                    'X': X,
                    'Y': Y,
                    '_solution': solution  # 内部保存用于验证
                }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        matrix = question_case['matrix']
        n, m = question_case['n'], question_case['m']
        matrix_str = '\n'.join(' '.join(map(str, row)) for row in matrix)
        return f"""Koa the Koala has a {n}x{m} matrix with distinct numbers 1-{n*m}. Find a matrix A' where:

1. S(A') = S(A) (same row/column max sets)
2. All rows/columns are bitonic
3. Output format: n lines with m numbers, or -1

Input:
{n} {m}
{matrix_str}

Output your answer within [answer] and [/answer] tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _generate_solution(original):
        """参考代码算法实现，返回解矩阵或None"""
        n, m = len(original), len(original[0])
        c = dict()  # 行最大值标记
        r = dict()  # 列最大值标记

        # 计算原矩阵的行和列最大值
        for i in range(n):
            max_row = max(original[i])
            c[max_row] = True
        for j in range(m):
            max_col = max(original[i][j] for i in range(n))
            r[max_col] = True

        ans = [[0]*m for _ in range(n)]
        q = deque()
        x = 0
        y = 0

        for num in range(n*m, 0, -1):
            is_row_max = c.get(num, False)
            is_col_max = r.get(num, False)
            x += is_row_max
            y += is_col_max

            if is_row_max or is_col_max:
                ans_x = x - 1
                ans_y = y - 1
                ans[ans_x][ans_y] = num
                # 填充队列
                if is_row_max:
                    for j in range(ans_y-1, -1, -1):
                        q.append( (ans_x, j) )
                if is_col_max:
                    for i in range(ans_x-1, -1, -1):
                        q.append( (i, ans_y) )
            else:
                if not q:
                    return None  # 无解
                i, j = q.popleft()
                ans[i][j] = num

        # 验证生成的解矩阵
        if Drearrangebootcamp._validate_solution(ans, original):
            return ans
        return None

    @classmethod
    def _validate_solution(cls, solution, original):
        """验证解矩阵是否满足所有条件"""
        # 元素唯一性
        flat = [num for row in solution for num in row]
        if len(set(flat)) != len(flat) or set(flat) != set(range(1, len(flat)+1)):
            return False

        # Bitonic验证
        for row in solution:
            if not cls.is_bitonic(row):
                return False
        for col in zip(*solution):
            if not cls.is_bitonic(col):
                return False

        # 谱集验证
        X_sol = {max(row) for row in solution}
        Y_sol = {max(col) for col in zip(*solution)}
        X_ori = {max(row) for row in original}
        Y_ori = {max(col) for col in zip(*original)}
        return X_sol == X_ori and Y_sol == Y_ori

    @staticmethod
    def is_bitonic(arr):
        if len(arr) <= 1:
            return True
        peak = arr.index(max(arr))
        # 递增部分
        for i in range(1, peak+1):
            if arr[i] <= arr[i-1]:
                return False
        # 递减部分
        for i in range(peak, len(arr)-1):
            if arr[i] <= arr[i+1]:
                return False
        return True
