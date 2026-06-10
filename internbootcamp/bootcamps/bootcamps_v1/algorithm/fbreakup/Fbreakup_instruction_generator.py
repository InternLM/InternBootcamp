import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque




class FbreakupInstructionGenerator(BaseInstructionGenerator):
    """Fbreakup Bootcamp指令生成器"""
    
    def __init__(self, node_range=(4,8), budget_range=(10, 100)):
        """
        初始化Fbreakup指令生成器
        
        Args:
            node_range: 参数描述
            budget_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数说明:
        node_range: 生成图的节点数量范围 (min, max)
        budget_range: 道路关闭预算范围 (min, max)
        """
        self.min_nodes, self.max_nodes = node_range
        self.min_budget, self.max_budget = budget_range
    
    def case_generator(self):
        # 随机选择案例类型：单边解/双边解/无解
        case_type = random.choices(
            ['single', 'double', 'impossible'], 
            weights=[45, 45, 10], 
            k=1
        )[0]

        if case_type == 'single':
            return self._generate_single_case()
        elif case_type == 'double':
            return self._generate_double_case()
        else:
            return self._generate_impossible_case()
    
    @staticmethod
    def prompt_func(question_case) -> str:
        roads = "\n".join(
            f"Road {i+1}: {x}-{y} (closure cost {w})" 
            for i, (x,y,w) in enumerate(question_case['roads'])
        )
        return f"""Cities {question_case['s']} and {question_case['t']} need to disconnect. 
Find up to 2 roads to close with minimal total cost.

Cities: {question_case['n']}
Roads:
{roads}

Output format:
[answer]
<total_cost>
<road_count>
<road_numbers>
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_single_case(self):
        """生成需要切断一条边的案例（链式结构）"""
        n = random.randint(self.min_nodes, self.max_nodes)
        s, t = 1, n
        roads = []
        for i in range(n-1):
            w = random.randint(self.min_budget, self.max_budget)
            roads.append( (i+1, i+2, w) )

        # 找预算最小的边
        min_idx, (x,y,min_w) = min(enumerate(roads), key=lambda x: x[1][2])
        return {
            'n': n,
            'm': n-1,
            's': s,
            't': t,
            'roads': roads,
            'expected': {
                'min_budget': min_w,
                'c': 1,
                'roads': [min_idx+1]  # 道路编号从1开始
            }
        }

    def _generate_double_case(self):
        """生成需要切断两条边的案例（并行双路径结构）"""
        # s=1, t=4
        roads = [
            (1,2, random.randint(10,50)),  # 路径1-边1
            (2,4, random.randint(10,50)),  # 路径1-边2
            (1,3, random.randint(10,50)),  # 路径2-边1
            (3,4, random.randint(10,50)),  # 路径2-边2
            (2,3, self.max_budget*2)       # 高成本边，不应被选
        ]
        # 最优解为选两条路径各一个最低成本边
        path1 = [roads[0][2], roads[1][2]]
        path2 = [roads[2][2], roads[3][2]]
        min1 = min(path1)
        min2 = min(path2)
        solution = {
            'min_budget': min1 + min2,
            'c': 2,
            'roads': [
                roads.index(r)+1 for r in roads 
                if r[2] in (min1, min2)
            ]
        }
        return {
            'n': 4,
            'm': 5,
            's': 1,
            't': 4,
            'roads': roads,
            'expected': solution
        }

    def _generate_impossible_case(self):
        """生成无法断开连接的案例"""
        return {
            'n': 3,
            'm': 4,
            's': 1,
            't': 3,
            'roads': [
                (1,2, 10), (2,3, 20),
                (1,3, 30), (1,3, 40)
            ],
            'expected': -1
        }

    @staticmethod
    def _is_disconnected(n, roads, s, t, deleted_roads):
        """判断删除指定边后是否断开连接"""
        deleted = set(deleted_roads)
        adj = [[] for _ in range(n+1)]
        for idx, (x,y,w) in enumerate(roads):
            if (idx+1) not in deleted:
                adj[x].append(y)
                adj[y].append(x)

        # BFS检查连通性
        visited = [False]*(n+1)
        queue = deque([s])
        visited[s] = True
        while queue:
            u = queue.popleft()
            if u == t:
                return False
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)
        return True
