import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from itertools import combinations




class CpartyRewardCalculator(BaseRewardCalculator):
    """Cparty奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强鲁棒性的答案提取"""
        matches = re.findall(r'\[answer\][\s]*((?:\d+[\s\n]*)+)[\s]*\[/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        
        # 取最后一个答案块并解析
        content = matches[-1].strip()
        parts = [p for p in re.split(r'\s+', content) if p]
        
        try:
            if len(parts) < 1:
                return None
            steps = int(parts[0])
            guests = list(map(int, parts[1:1+steps])) if steps >0 else []
            if len(guests) != steps:
                return None
            return (steps, guests)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        """严格模拟验证的改进版本"""
        if not solution or solution[0] != case['min_steps']:
            return False
        
        n = case['n']
        edges = case['edges']
        selected = solution[1]

        # 构建初始邻接矩阵
        adj = [set() for _ in range(n+1)]  # 1-based索引
        for u, v in edges:
            adj[u].add(v)
            adj[v].add(u)
        
        # 初始自反关系
        for u in range(1, n+1):
            adj[u].add(u)
        
        # 模拟操作流程
        for guest in selected:
            friends = adj[guest].copy()
            # 将所有朋友两两连接
            new_edges = combinations(friends, 2)
            for u, v in new_edges:
                adj[u].add(v)
                adj[v].add(u)
        
        # 验证全连接
        full_set = set(range(1, n+1))
        return all(adj[u] == full_set for u in range(1, n+1))
    
    # 其他额外方法

