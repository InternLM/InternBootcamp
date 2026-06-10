import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import deque




class CandryushaandcoloredballoonsRewardCalculator(BaseRewardCalculator):
    """Candryushaandcoloredballoons奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        lines = last_answer.split('\n')
        if len(lines) < 2:
            return None
        try:
            k = int(lines[0].strip())
            colors = list(map(int, lines[1].strip().split()))
            return {'k': k, 'colors': colors}
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or 'k' not in solution or 'colors' not in solution:
            return False
        user_k = solution['k']
        user_colors = solution['colors']
        n = identity['n']
        edges = identity['edges']
        if len(user_colors) != n:
            return False
        adj = [[] for _ in range(n+1)]
        for x, y in edges:
            adj[x].append(y)
            adj[y].append(x)
        max_degree = max(len(nodes) for nodes in adj[1:n+1])
        correct_k = max_degree + 1
        if user_k != correct_k:
            return False
        if any(c < 1 or c > user_k for c in user_colors):
            return False
        color_of = {i: user_colors[i-1] for i in range(1, n+1)}
        for b in range(1, n+1):
            neighbors = adj[b]
            for i in range(len(neighbors)):
                a = neighbors[i]
                for j in range(i+1, len(neighbors)):
                    c = neighbors[j]
                    a_color = color_of[a]
                    b_color = color_of[b]
                    c_color = color_of[c]
                    if a_color == b_color or a_color == c_color or b_color == c_color:
                        return False
        return True
    
    # 其他额外方法

