import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict




class CsergeysproblemRewardCalculator(BaseRewardCalculator):
    """Csergeysproblem奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        numbers = re.findall(r'\d+', content)
        if len(numbers) < 1:
            return None
        try:
            k = int(numbers[0])
            if len(numbers) != k + 1:
                return None
            solution = list(map(int, numbers[1:]))
            if len(solution) != len(set(solution)):
                return None
            return solution
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            if not isinstance(solution, list):
                return False
            q = list(map(int, solution))
            if len(q) != len(set(q)):
                return False
        except:
            return False

        n = identity['n']
        edges = identity['edges']
        q_set = set(q)
        if any(x < 1 or x > n for x in q):
            return False

        for a, b in edges:
            if a in q_set and b in q_set:
                return False

        adj = defaultdict(list)
        for a, b in edges:
            adj[a].append(b)

        coverage = set()
        for x in q_set:
            step1 = adj.get(x, [])
            step2 = []
            for u in step1:
                step2.extend(adj.get(u, []))
            coverage.update(step1)
            coverage.update(step2)

        all_vertices = set(range(1, n+1))
        z_vertices = all_vertices - q_set
        for z in z_vertices:
            if z not in coverage:
                return False
        return True
    
    # 其他额外方法

