import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque




class DstrangehousingInstructionGenerator(BaseInstructionGenerator):
    """Dstrangehousing Bootcamp指令生成器"""
    
    def __init__(self, max_houses=10, max_paths=15):
        """
        初始化Dstrangehousing指令生成器
        
        Args:
            max_houses: 参数描述
            max_paths: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_houses = max_houses
        self.max_paths = max_paths
    
    def case_generator(self):
        # 生成连通二分图或不可解图（概率各50%）
        if random.random() < 0.5:
            return self._generate_valid_case()
        else:
            return self._generate_invalid_case()
    
    @staticmethod
    def prompt_func(case) -> str:
        edges = "\n".join(f"{u} {v}" for u, v in case['edges'])
        return f"""# 冬季信息学校的教师住房问题

## 问题描述
需要选择若干房屋安排教师，满足：
1. 任何两个有教师的房屋不能直接相连
2. 无教师的房屋之间的通道关闭后，剩余通道必须保持全图连通
3. 必须同时满足上述两个条件

## 输入格式
房屋数：{case['n']}
通道数：{case['m']}
通道列表：
{edges}

## 输出要求
若存在可行方案：
[answer]
YES
K
a₁ a₂ ... a_K
[/answer]

若无解：
[answer]
NO
[/answer]

请严格遵循输出格式，答案标记必须使用[answer]标签。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_case(self):
        """生成保证有解的连通二分图"""
        n = random.randint(3, self.max_houses)
        partition = {i: i%2 for i in range(1, n+1)}  # 简单二分

        # 确保图连通
        edges = []
        visited = set([1])
        queue = deque([1])

        while len(visited) < n:
            u = queue.popleft()
            candidates = [v for v in range(1, n+1) 
                        if v not in visited and partition[v] != partition[u]]
            if candidates:
                v = random.choice(candidates)
                edges.append((u, v))
                visited.add(v)
                queue.append(v)
            else:  # 添加跨分区边保持连通
                for v in range(1, n+1):
                    if v not in visited and partition[v] == partition[u]:
                        edges.append((u, v))
                        visited.add(v)
                        queue.append(v)
                        break

        # 添加额外边（保持二分性）
        possible_edges = []
        for u in range(1, n):
            for v in range(u+1, n+1):
                if partition[u] != partition[v] and (u, v) not in edges:
                    possible_edges.append((u, v))

        add_num = min(len(possible_edges), self.max_paths - len(edges))
        edges.extend(random.sample(possible_edges, add_num))

        return {'n': n, 'm': len(edges), 'edges': edges}

    def _generate_invalid_case(self):
        """生成包含奇数环的不可解案例"""
        cycle_size = random.choice([3, 5, 7])
        n = cycle_size
        edges = [(i, i%cycle_size +1) for i in range(1, cycle_size+1)]

        # 添加额外边保持连通
        for _ in range(random.randint(0, 3)):
            u = random.randint(1, n)
            v = random.randint(1, n)
            if u != v and (u, v) not in edges and (v, u) not in edges:
                edges.append((u, v))

        return {'n': n, 'm': len(edges), 'edges': edges}

    @classmethod
    def _is_bipartite(cls, edges, n):
        """判断是否为二分图（可解条件）"""
        color = {}
        adj = {u: [] for u in range(1, n+1)}
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        for u in range(1, n+1):
            if u not in color:
                queue = deque([u])
                color[u] = 0
                while queue:
                    current = queue.popleft()
                    for neighbor in adj[current]:
                        if neighbor not in color:
                            color[neighbor] = color[current] ^ 1
                            queue.append(neighbor)
                        elif color[neighbor] == color[current]:
                            return False
        return True
