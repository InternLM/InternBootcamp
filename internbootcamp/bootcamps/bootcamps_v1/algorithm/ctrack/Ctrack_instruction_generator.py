import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from heapq import heappop
from heapq import heappush

# === 源文件中的全局函数 ===

def manhattan(r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2)

def solve(n, m, k, mat):
    start = None
    end = None
    for i in range(n):
        for j in range(m):
            if mat[i][j] == 'S':
                start = (i, j)
            elif mat[i][j] == 'T':
                end = (i, j)
    if not start or not end:
        return "-1"
    br, bc = start
    er, ec = end

    heap = []
    initial_priority = manhattan(br, bc, er, ec)
    heappush(heap, (initial_priority, '', 0, br, bc, 0, ''))
    ha = {i: {j: set() for j in range(m)} for i in range(n)}

    while heap:
        priority, path, steps, r, c, cu, used_str = heappop(heap)
        if (r, c) == (er, ec):
            return path
        if used_str in ha[r][c]:
            continue
        ha[r][c].add(used_str)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m:
                ch = mat[nr][nc]
                if ch == 'S':
                    continue
                new_steps = steps + 1
                new_priority = new_steps + manhattan(nr, nc, er, ec)
                if ch == 'T':
                    heappush(heap, (new_priority, path, new_steps, nr, nc, cu, used_str))
                else:
                    if ch in used_str:
                        new_used = used_str
                        new_cu = cu
                    else:
                        new_cu = cu + 1
                        if new_cu > k:
                            continue
                        new_used = ''.join(sorted(set(used_str) | {ch}))
                    new_path = path + ch
                    if new_used not in ha[nr][nc]:
                        heappush(heap, (new_priority, new_path, new_steps, nr, nc, new_cu, new_used))
    return "-1"


class CtrackInstructionGenerator(BaseInstructionGenerator):
    """Ctrack Bootcamp指令生成器"""
    
    def __init__(self, n=5, m=3, k=2, max_attempts=100):
        """
        初始化Ctrack指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
            k: 参数描述
            max_attempts: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.m = m
        self.k = k
        self.max_attempts = max_attempts
    
    def case_generator(self):
        for _ in range(self.max_attempts):
            while True:
                s_pos = (random.randint(0, self.n-1), random.randint(0, self.m-1))
                t_pos = (random.randint(0, self.n-1), random.randint(0, self.m-1))
                if s_pos != t_pos:
                    break

            map_data = [
                [
                    'S' if (i, j) == s_pos else
                    'T' if (i, j) == t_pos else
                    random.choice('abcdefghijklmnopqrstuvwxyz')
                    for j in range(self.m)
                ]
                for i in range(self.n)
            ]
            map_data = [''.join(row) for row in map_data]

            expected_output = solve(self.n, self.m, self.k, map_data)
            if expected_output != '-1':
                return {
                    'n': self.n,
                    'm': self.m,
                    'k': self.k,
                    'map': map_data,
                    'expected_output': expected_output
                }
        raise ValueError("Failed to generate valid case after multiple attempts")
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        k = question_case['k']
        map_data = question_case['map']
        input_example = f"{n} {m} {k}\n" + "\n".join(map_data)
        prompt = f"""你是冬季两项比赛的路径规划专家，请帮助Valery找到从起点S到终点T的最短路径。路径需要满足以下规则：

1. 移动规则：每次只能移动到相邻的单元格（上下左右），不能越界。
2. 类型限制：路径中经过的不同单元格类型（小写字母）的数量不能超过{k}个。S和T不计入类型且不能重复访问。
3. 最短且字典序最小：在满足条件的最短路径中，选择字典序最小的路径。路径的字典序比较基于各单元格类型的字符顺序。

输入格式：
第一行包含三个整数n、m、k。
接下来n行，每行m个字符表示地图，包含恰好一个S和一个T。

输出格式：
如果存在合法路径，输出路径字符串（不包含S和T的字符）。否则输出-1。

当前谜题实例：
{input_example}

请将你的答案放在[answer]和[/answer]标签之间。例如：[answer]abc[/answer] 或 [answer]-1[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

