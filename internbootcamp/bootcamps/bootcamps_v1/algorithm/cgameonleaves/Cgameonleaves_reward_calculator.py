import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict




class CgameonleavesRewardCalculator(BaseRewardCalculator):
    """Cgameonleaves奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(Ayush|Ashish)\s*\[/answer\]', output, re.IGNORECASE)
        return matches[-1].strip().title() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        x = identity['x']
        edges = identity['edges']
        
        # 计算特殊节点x的度数
        degree = sum(1 for u, v in edges if u == x or v == x)
        
        # 胜负判定规则
        if n == 1:
            correct = "Ayush"
        elif degree <= 1:
            correct = "Ayush" if (n % 2 == 1) else "Ashish"
        else:
            total_moves = (n - degree - 1) + degree  # 等效n-1
            correct = "Ashish" if (total_moves % 2 == 0) else "Ayush"
        
        return solution.strip().lower() == correct.lower()
    
    # 其他额外方法

