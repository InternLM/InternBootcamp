import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DchemicaltableRewardCalculator(BaseRewardCalculator):
    """Dchemicaltable奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强提取鲁棒性：处理小数点、中文数字等
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        last_match = matches[-1].strip()
        # 提取所有数字字符
        digits = re.sub(r'\D', '', last_match)
        return digits if digits else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        class OptimizedUnionFind:
            __slots__ = ['parent', 'count']
            def __init__(self, size):
                self.parent = list(range(size+1))
                self.count = size  # 初始连通分量数
            
            def find(self, x):
                while self.parent[x] != x:
                    self.parent[x] = self.parent[self.parent[x]]  # 路径压缩优化
                    x = self.parent[x]
                return x
            
            def union(self, x, y):
                fx = self.find(x)
                fy = self.find(y)
                if fx != fy:
                    # 小树合并到大树优化
                    if fx > fy:
                        fx, fy = fy, fx
                    self.parent[fx] = fy
                    self.count -= 1

        n = identity['n']
        m = identity['m']
        uf = OptimizedUnionFind(n + m)
        
        # 转换坐标为并查集节点
        for r, c in identity['elements']:
            uf.union(r, c + n)
        
        try:
            return int(solution) == (uf.count - 1)
        except (ValueError, TypeError):
            return False
    
    # 其他额外方法

