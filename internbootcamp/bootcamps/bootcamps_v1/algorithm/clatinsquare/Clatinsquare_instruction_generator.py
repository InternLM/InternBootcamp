import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import json
from random import randint
from random import choices
from random import shuffle
import random




class ClatinsquareInstructionGenerator(BaseInstructionGenerator):
    """Clatinsquare Bootcamp指令生成器"""
    
    def __init__(self, default_n=3, default_m=5, n_range=(3, 5), m_range=(5, 10)):
        """
        初始化Clatinsquare指令生成器
        
        Args:
            default_n: 参数描述
            default_m: 参数描述
            n_range: 参数描述
            m_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.default_n = default_n
        self.default_m = default_m
        self.n_range = n_range
        self.m_range = m_range
    
    def case_generator(self):
        # 生成随机矩阵大小
        n = randint(*self.n_range) if isinstance(self.n_range, tuple) else self.default_n
        
        # 生成基础矩阵（单位循环矩阵）
        base_matrix = []
        for i in range(n):
            if i == 0:
                row = list(range(1, n+1))
            else:
                row = base_matrix[i-1][-1:] + base_matrix[i-1][:-1]
            base_matrix.append(row)
        
        # 生成随机操作序列以打乱基础矩阵
        shuffle_ops = ''.join(choices('RLDUIC', k=randint(5, 10)))
        # 应用操作生成初始矩阵
        shuffled_matrix = self._compute_final(n, base_matrix, shuffle_ops)
        
        # 生成测试用例的操作序列
        m = randint(*self.m_range) if isinstance(self.m_range, tuple) else self.default_m
        operations = ''.join(choices('RLDUIC', k=m))
        
        return {
            'n': n,
            'm': m,
            'matrix': shuffled_matrix,
            'operations': operations
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        matrix = question_case['matrix']
        ops = question_case['operations']
        matrix_str = '\n'.join(' '.join(map(str, row)) for row in matrix)
        
        op_def = """操作定义如下：
- R：所有列向右循环移动一位（例如列1→2，列n→1）
- L：所有列向左循环移动一位（列1→n，列2→1）
- D：所有行向下循环移动一位（行1→2，行n→1）
- U：所有行向上循环移动一位（行1→n，行2→1）
- I：将每行的排列取逆（例如行[2,3,1]的逆是[3,1,2]，因为原排列中位置1是2，逆排列中2的位置是1）
- C：将每列的排列取逆（列元素的排列取逆后重新放置）"""
        
        return f"""给定一个 {n}x{n} 矩阵，其中每行每列均为1到{n}的排列。执行以下{m}个操作后输出最终矩阵：

{op_def}

输入格式：
1
{n} {m}
{matrix_str}
{ops}

请输出执行所有操作后的矩阵，格式为{n}行，每行{n}个整数，放在[answer]标签内。例如：

[answer]
2 3 1 
3 1 2 
1 2 3 
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _compute_final(cls, n, initial_matrix, operations):
        # 转换为0-based索引
        v = [[x-1 for x in row] for row in initial_matrix]
        e = [0, 0, 0]  # 行、列、值的偏移量
        p = [0, 1, 2]  # 映射顺序：行、列、值

        for c in operations:
            if c == 'R':
                e[p[1]] = (e[p[1]] + 1) % n
            elif c == 'L':
                e[p[1]] = (e[p[1]] - 1) % n
            elif c == 'D':
                e[p[0]] = (e[p[0]] + 1) % n
            elif c == 'U':
                e[p[0]] = (e[p[0]] - 1) % n
            elif c == 'I':
                p[1], p[2] = p[2], p[1]  # 交换列和值的映射
            elif c == 'C':
                p[0], p[2] = p[2], p[0]  # 交换行和值的映射

        # 生成最终矩阵
        w = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                # 原始坐标和值
                z = [i, j, v[i][j]]
                # 应用偏移和映射后的坐标
                I = (z[p[0]] + e[p[0]]) % n
                J = (z[p[1]] + e[p[1]]) % n
                K = (z[p[2]] + e[p[2]]) % n
                w[I][J] = K + 1  # 转换回1-based
        return w
