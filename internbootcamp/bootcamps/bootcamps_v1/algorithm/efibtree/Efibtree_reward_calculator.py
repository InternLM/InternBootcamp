import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class EfibtreeRewardCalculator(BaseRewardCalculator):
    """Efibtree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        answer = matches[-1].strip().upper()
        return answer if answer in {'YES', 'NO'} else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        edges = identity['edges']
        
        # 快速判断标记案例
        if 'expected' in identity:
            return solution == identity['expected']
        
        # 构建邻接表
        adj = [[] for _ in range(n+1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        
        # 预计算斐波那契序列
        fib = [1, 1]
        while fib[-1] < n:
            fib.append(fib[-1] + fib[-2])
        if n not in fib:
            return solution == 'NO'
        k = fib.index(n)
        
        # 改进的递归验证算法
        def validate(root, parent):
            size = 1
            valid_splits = []
            
            for child in adj[root]:
                if child == parent:
                    continue
                child_size = validate(child, root)
                if child_size == -1:
                    return -1
                size += child_size
                valid_splits.append(child_size)
            
            # 基准情况
            if size == 1:
                return 1
            
            # 检查当前子树是否可分割
            required = [fib[k-1], fib[k-2]]
            for s in valid_splits:
                if s in required:
                    remaining = size - 1 - s  # 减去当前根节点
                    if remaining in required:
                        return size
            return -1
        
        return (solution == 'YES') == (validate(1, -1) != -1)
    
    # 其他额外方法

