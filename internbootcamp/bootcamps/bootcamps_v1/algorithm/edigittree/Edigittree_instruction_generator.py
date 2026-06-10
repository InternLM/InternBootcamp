import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
import math
from collections import deque
from itertools import combinations




class EdigittreeInstructionGenerator(BaseInstructionGenerator):
    """Edigittree Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Edigittree指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = params.get('n_min', 2)
        self.n_max = params.get('n_max', 8)  # 适当提高上限仍保证暴力验证可行
        self.m_max = params.get('m_max', 100)
    
    def case_generator(self):
        # 生成符合要求的M
        M = self._valid_m_generator()
        n = random.randint(self.n_min, self.n_max)
        
        # 生成规范化的树结构
        edges = self._generate_tree(n)
        
        # 暴力验证答案
        def compute_expected(n_val, m_val, edges_list):
            # 构建邻接表
            adj = [[] for _ in range(n_val)]
            for u, v, w in edges_list:
                adj[u].append((v, w))
                adj[v].append((u, w))
            
            # 预处理所有节点对
            count = 0
            for u, v in combinations(range(n_val), 2):
                # 双向路径查找
                for src, dst in [(u, v), (v, u)]:
                    # BFS找路径
                    visited = {src: None}
                    q = deque([src])
                    while q:
                        node = q.popleft()
                        if node == dst:
                            break
                        for neighbor, weight in adj[node]:
                            if neighbor not in visited:
                                visited[neighbor] = (node, weight)
                                q.append(neighbor)
                    
                    # 提取路径数字
                    path = []
                    current = dst
                    while visited.get(current) is not None:
                        prev_node, weight = visited[current]
                        path.append(weight)
                        current = prev_node
                    num = 0
                    for digit in reversed(path):
                        num = num * 10 + digit
                        num %= m_val
                    if num % m_val == 0:
                        count += 1
            return count
        
        expected = compute_expected(n, M, edges)
        
        return {
            'n': n,
            'M': M,
            'edges': edges,
            'expected_answer': expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [f"{question_case['n']} {question_case['M']}"]
        for edge in question_case['edges']:
            input_lines.append(f"{edge[0]} {edge[1]} {edge[2]}")
        input_str = '\n'.join(input_lines)
        
        prompt = f"""Given a tree with {question_case['n']} vertices where each edge contains a digit (1-9), find the number of ordered pairs (u, v), u≠v, such that the decimal number formed by the path from u to v is divisible by {question_case['M']}.

Input format:
First line: n M
Next n-1 lines: u v w (edge between u and v with digit w)

Example valid output format:
The answer is [answer]42[/answer] where 42 is the correct count.

Your Input:
{input_str}

Calculate the answer and put your final numerical answer within [answer] tags."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _valid_m_generator(self):
        """生成与10互质的M，包含边界情况处理"""
        candidates = [1]  # 特殊情况M=1
        for _ in range(100):
            m = random.randint(2, self.m_max)
            if math.gcd(m, 10) == 1:
                candidates.append(m)
        return random.choice(candidates)

    def _generate_tree(self, n):
        """更健壮的树生成算法，覆盖链状和星型结构"""
        if random.random() < 0.3:  # 30%概率生成链状树
            edges = []
            for i in range(1, n):
                edges.append((i-1, i, random.randint(1,9)))
            return edges
        else:  # 常规随机树
            edges = []
            nodes = list(range(n))
            random.shuffle(nodes)
            for i in range(1, n):
                u = random.choice(nodes[:i])
                v = nodes[i]
                edges.append((u, v, random.randint(1,9)))
            return edges
