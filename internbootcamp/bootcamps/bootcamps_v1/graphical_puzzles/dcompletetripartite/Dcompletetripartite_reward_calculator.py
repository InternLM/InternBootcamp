import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class DcompletetripartiteRewardCalculator(BaseRewardCalculator):
    """Dcompletetripartite奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 快速拒绝错误格式
        if not solution or solution.strip() == "-1":
            return False
        
        try:
            labels = list(map(int, solution.split()))
        except ValueError:
            return False
        
        # 验证基础条件
        if len(labels) != identity['n']:
            return False
        if not all(l in {1,2,3} for l in labels):
            return False
        
        # 构建分组映射
        groups = {1: set(), 2: set(), 3: set()}
        for v, l in enumerate(labels, 1):
            groups[l].add(v)
        
        # 检查非空子集
        if any(len(groups[i]) == 0 for i in [1,2,3]):
            return False
        
        # 验证边约束
        edge_set = set(map(tuple, identity['edges']))
        
        # 验证每个子集的内部无连接
        for group in groups.values():
            for a in group:
                for b in group:
                    if a < b and (a, b) in edge_set:
                        return False
        
        # 验证跨子集的完全连接
        expected_pairs = [
            (groups[1], groups[2]),
            (groups[2], groups[3]),
            (groups[3], groups[1])
        ]
        for s1, s2 in expected_pairs:
            for a in s1:
                for b in s2:
                    if a > b:
                        a, b = b, a
                    if (a, b) not in edge_set:
                        return False
        
        return True
    
    # 其他额外方法

