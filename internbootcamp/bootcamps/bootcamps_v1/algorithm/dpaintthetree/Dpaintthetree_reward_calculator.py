import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from itertools import permutations
from collections import defaultdict




class DpaintthetreeRewardCalculator(BaseRewardCalculator):
    """Dpaintthetree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer_block = matches[-1].strip()
        lines = [line.strip() for line in answer_block.split('\n') if line.strip()]
        
        if not lines or lines[0] == '-1':
            return {'cost': -1, 'colors': None}
        
        try:
            cost = int(lines[0])
            colors = []
            if len(lines) >= 2:
                colors = list(map(int, lines[1].split()))
                if any(c not in {1,2,3} for c in colors):
                    return None
            return {'cost': cost, 'colors': colors}
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        
        # 预期无解的情况验证
        if identity['expected_cost'] == -1:
            return solution.get('cost') == -1 and solution.get('colors') is None
        
        # 成本验证
        if solution['cost'] != identity['expected_cost']:
            return False
        
        # 颜色序列验证
        colors = solution['colors']
        if len(colors) != identity['n'] or any(c not in {1,2,3} for c in colors):
            return False
        
        # 全局路径检查
        adj = defaultdict(list)
        for u, v in identity['edges']:
            adj[u].append(v)
            adj[v].append(u)
        
        # 寻找路径端点
        start = None
        for node in adj:
            if len(adj[node]) == 1:
                start = node
                break
        
        # 遍历路径生成顺序
        path = []
        visited = set()
        stack = [(start, None)]
        while stack:
            node, parent = stack.pop()
            visited.add(node)
            path.append(node)
            neighbors = [n for n in adj[node] if n != parent]
            if neighbors:
                stack.append((neighbors[0], node))
        
        # 检查连续三元组
        for i in range(len(path)-2):
            a, b, c = colors[path[i]-1], colors[path[i+1]-1], colors[path[i+2]-1]
            if len({a, b, c}) < 3:
                return False
        
        return True
    
    # 其他额外方法

