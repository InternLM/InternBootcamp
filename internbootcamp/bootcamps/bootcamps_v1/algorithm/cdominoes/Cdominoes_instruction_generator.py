import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import math
from collections import defaultdict




class CdominoesInstructionGenerator(BaseInstructionGenerator):
    """Cdominoes Bootcamp指令生成器"""
    
    def __init__(self, n=2, m=3):
        """
        初始化Cdominoes指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.m = m
    
    def case_generator(self):
        # 生成合法多米诺配置
        domino_set = self.generate_valid_set()
        optimal_matrix = self.build_optimal_matrix(domino_set)
        input_matrix = self.scramble_matrix(optimal_matrix)
        
        # 计算理论最优值
        total_S = sum(int(a)+int(b) for row in input_matrix for a,b in row)
        optimal_max = math.ceil(total_S / (2 * self.m))
        
        return {
            'input_matrix': input_matrix,
            'optimal_matrix': optimal_matrix,
            'n': self.n,
            'm': self.m,
            'optimal_max': optimal_max,
        }
    
    @staticmethod
    def prompt_func(question_case):
        matrix = question_case['input_matrix']
        return f"""Rearrange the {question_case['n']}x{2*question_case['m']} domino matrix to minimize maximum column sum. Original matrix:
""" + '\n'.join(' '.join(row) for row in matrix) + """

Rules:
1. Keep dominoes horizontal but can rotate
2. Reorder dominoes within each row
3. Format answer with {question_case['n']} lines of {question_case['m']} dominoes

Put your answer between [answer] and [/answer] tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_valid_set(self):
        """生成包含可优化空间的有效集合"""
        total = self.n * self.m
        while True:
            types = ['00', '01', '10', '11']
            probs = [0.25, 0.25, 0.25, 0.25]
            dominoes = random.choices(types, weights=probs, k=total)
            if sum(1 for d in dominoes if d in ['01','10']) > 0:
                return dominoes

    def build_optimal_matrix(self, domino_set):
        """按照官方解题算法构建最优矩阵"""
        # 统计类型
        k = defaultdict(int)
        for d in domino_set:
            if d in ['00','11']:
                k[d] += 1
            else:
                k['mix'] += 1

        # 初始化二维矩阵
        matrix = [[] for _ in range(self.n)]

        # 类型划分（参考官方解法）
        a = k['11'] // self.n
        b = (k['mix'] // 2) // self.n
        c = k['00'] // self.n

        # 基础分配
        for row in matrix:
            row += ['11']*a
            row += ['01']*b
            row += ['10']*b
            row += ['00']*c

        # 余数处理
        rem_11 = k['11'] % self.n
        rem_mix = k['mix'] % (2*self.n)
        rem_00 = k['00'] % self.n

        # Phase 1: 分配余数11
        for i in range(rem_11):
            matrix[i].append('11')

        # Phase 2: 分配余数mix
        for i in range(rem_mix):
            matrix[i%self.n].append('01' if i%2 else '10')

        # Phase 3: 分配余数00
        for i in range(rem_00):
            matrix[i].append('00')

        # 填充并校验每行长度
        for row in matrix:
            random.shuffle(row)
            while len(row) < self.m:
                # 异常处理：补充虚拟domino（理论上不应触发）
                row.append('00')
            del row[self.m:]  # 精确截断

        return matrix

    def scramble_matrix(self, matrix):
        """生成随机输入矩阵"""
        scrambled = []
        for row in matrix:
            new_row = []
            for d in row:
                if d in ['01','10']:
                    new_row.append(random.choice([d, d[::-1]]))
                else:
                    new_row.append(d)
            random.shuffle(new_row)
            scrambled.append(new_row)
        return scrambled
