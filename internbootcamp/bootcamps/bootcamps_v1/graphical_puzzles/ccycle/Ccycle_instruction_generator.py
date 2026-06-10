import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CcycleInstructionGenerator(BaseInstructionGenerator):
    """Ccycle Bootcamp指令生成器"""
    
    def __init__(self, n=5, has_cycle=True):
        """
        初始化Ccycle指令生成器
        
        Args:
            n: 参数描述
            has_cycle: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.has_cycle = has_cycle
    
    def case_generator(self):
        n = self.n
        has_cycle = self.has_cycle

        # 处理n < 3的情况，无法形成环
        if n < 3 and has_cycle:
            print("Warning: For n < 3, a cycle of length 3 is impossible. Setting has_cycle to False.")
            has_cycle = False

        adj_matrix = []
        if has_cycle:
            # 初始化一个n x n的矩阵，初始为0
            matrix = [[0 for _ in range(n)] for _ in range(n)]
            # 随机选择三个顶点形成环
            if n >= 3:
                # 随机选择三个不同的顶点
                vertices = random.sample(range(n), 3)
                a, b, c = vertices
                # 构造环：a→b, b→c, c→a
                matrix[a][b] = 1
                matrix[b][c] = 1
                matrix[c][a] = 1
                # 处理其他顶点与环顶点之间的关系
                for i in range(n):
                    if i not in vertices:
                        # 选择i与环顶点的连接方式，这里假设i胜过环中的两个顶点，输给另一个
                        # 这只是一个示例，具体可根据需要调整
                        for j in vertices:
                            if j == a:
                                matrix[i][j] = 1  # i胜过a
                            elif j == b:
                                matrix[i][j] = 1  # i胜过b
                            else:
                                matrix[j][i] = 1  # c胜过i
                        # 处理i与其他非环顶点
                        for j in range(i + 1, n):
                            if j not in vertices:
                                matrix[i][j] = 1  # i胜过j
                # 处理非环顶点之间的关系
                for i in range(n):
                    for j in range(i + 1, n):
                        if i not in vertices and j not in vertices:
                            matrix[i][j] = 1  # i胜过j
            else:
                # 当n <3时，无法形成环，设置为无环
                has_cycle = False
                matrix = [[0 for _ in range(n)] for _ in range(n)]
                for i in range(n):
                    for j in range(i + 1, n):
                        matrix[i][j] = 1
        else:
            # 传递锦标赛，i < j则i→j
            matrix = [[0 for _ in range(n)] for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n):
                    matrix[i][j] = 1

        # 将矩阵转换为字符串列表
        adj_str = [''.join(map(str, row)) for row in matrix]
        case = {
            'n': n,
            'adj_matrix': adj_str,
            'has_cycle': has_cycle,
            'cycle_vertices': vertices if has_cycle and n >=3 else None
        }
        return case
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        adj_matrix = question_case['adj_matrix']
        prompt = "你正在分析一个包含{}个顶点的锦标赛有向图。锦标赛的性质是，对于任意两个不同的顶点u和v，恰好存在一条有向边，要么u→v，要么v→u。你的任务是找出三个顶点a1, a2, a3，使得a1→a2，a2→a3，a3→a1。如果不存在这样的环，输出-1。请将你的答案放在[answer]和[/answer]标签之间。".format(n)
        prompt += "\n\n顶点的邻接矩阵如下：\n"
        for i in range(n):
            prompt += "顶点 {} 的邻接字符串：{}\n".format(i + 1, adj_matrix[i])
        prompt += "\n例如，输出可能是：\n[answer]1 3 2[/answer]\n或者\n[answer]-1[/answer]"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

