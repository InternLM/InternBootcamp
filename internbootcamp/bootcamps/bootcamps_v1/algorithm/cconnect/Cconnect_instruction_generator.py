import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CconnectInstructionGenerator(BaseInstructionGenerator):
    """Cconnect Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cconnect指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 5)  # 默认网格大小为5x5
    
    def case_generator(self):
        n = self.n
        # 随机生成起点和终点，确保它们不同
        r1, c1 = random.randint(1, n), random.randint(1, n)
        r2, c2 = random.randint(1, n), random.randint(1, n)
        while (r1, c1) == (r2, c2):
            r2, c2 = random.randint(1, n), random.randint(1, n)
        
        # 生成网格
        grid = []
        for _ in range(n):
            row = []
            for _ in range(n):
                row.append('0' if random.random() < 0.7 else '1')  # 调整概率，增加陆地数量
            grid.append(''.join(row))
        
        # 确保起点和终点是陆地
        grid[r1-1] = grid[r1-1][:c1-1] + '0' + grid[r1-1][c1:]
        grid[r2-1] = grid[r2-1][:c2-1] + '0' + grid[r2-1][c2:]
        
        grid_list = [list(row) for row in grid]
        
        # 计算连通区域
        start = (r1-1, c1-1)
        end = (r2-1, c2-1)
        
        parent = {}
        for i in range(n):
            for j in range(n):
                if grid_list[i][j] == '0':
                    parent[(i, j)] = (i, j)
        
        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]  # 路径压缩
                u = parent[u]
            return u
        
        def union(u, v):
            pu = find(u)
            pv = find(v)
            if pu != pv:
                parent[pv] = pu
        
        # 构建并查集
        for i in range(n):
            for j in range(n):
                if grid_list[i][j] == '0':
                    if i < n-1 and grid_list[i+1][j] == '0':
                        union((i, j), (i+1, j))
                    if j < n-1 and grid_list[i][j+1] == '0':
                        union((i, j), (i, j+1))
        
        start_root = find(start)
        end_root = find(end)
        
        if start_root == end_root:
            min_cost = 0
        else:
            region_a = [ (i, j) for i in range(n) for j in range(n) if grid_list[i][j] == '0' and find((i,j)) == start_root ]
            region_b = [ (i, j) for i in range(n) for j in range(n) if grid_list[i][j] == '0' and find((i,j)) == end_root ]
            
            min_cost = float('inf')
            for a in region_a:
                for b in region_b:
                    cost = (a[0] - b[0])**2 + (a[1] - b[1])**2
                    if cost < min_cost:
                        min_cost = cost
        
        # 将grid转换为字符串列表
        grid = [''.join(row) for row in grid_list]
        
        return {
            'n': n,
            'start': (r1, c1),
            'end': (r2, c2),
            'grid': grid,
            'answer': min_cost
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        start = question_case['start']
        end = question_case['end']
        grid = question_case['grid']
        
        grid_str = '\n'.join(grid)
        
        prompt = f"在一个{n}×{n}的网格中，Alice住在位置({start[0]}, {start[1]})，想要移动到({end[0]}, {end[1]})。每个格子是陆地（0）或水（1）。Alice只能在陆地上移动，无法游泳。她可以创建最多一个隧道，连接两个陆地格子，费用是两个格子坐标差的平方和。如果不需要隧道，费用是0。网格如下：\n\n{grid_str}\n\n请计算最小费用，并将答案放在[answer]标签中。例如：[answer]10[/answer]"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

