import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict




class FnastyaandtimemachineRewardCalculator(BaseRewardCalculator):
    """Fnastyaandtimemachine奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) < 1:
            return None
        
        try:
            k = int(lines[0])
        except ValueError:
            return None
        
        if len(lines) != k + 1:
            return None
        
        solution = []
        for line in lines[1:]:
            parts = line.split()
            if len(parts) != 2:
                return None
            try:
                v = int(parts[0])
                t = int(parts[1])
                solution.append((v, t))
            except ValueError:
                return None
        
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        
        n = identity['n']
        edges = identity['edges']
        
        # 构建邻接表时增加双向验证
        adj = defaultdict(set)
        for u, v in edges:
            adj[u].add(v)
            adj[v].add(u)
        
        # 验证起点和终点
        if solution[0] != (1, 0) or solution[-1][0] != 1:
            return False
        
        # 验证所有节点被访问
        visited_nodes = {v for v, _ in solution}
        if visited_nodes != set(range(1, n+1)):
            return False
        
        # 时空坐标唯一性验证
        seen = set()
        prev_v, prev_t = solution[0]
        seen.add((prev_v, prev_t))
        
        for v, t in solution[1:]:
            if (v, t) in seen:
                return False
            seen.add((v, t))
            
            # 转移类型验证
            if v == prev_v:
                # 时间跳跃
                if t >= prev_t:
                    return False
            else:
                # 移动验证
                if t != prev_t + 1:
                    return False
                if v not in adj[prev_v]:
                    return False
            
            prev_v, prev_t = v, t
        
        return True
    
    # 其他额外方法

