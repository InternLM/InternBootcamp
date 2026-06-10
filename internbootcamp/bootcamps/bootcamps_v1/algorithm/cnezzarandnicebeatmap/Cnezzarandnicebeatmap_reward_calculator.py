import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CnezzarandnicebeatmapRewardCalculator(BaseRewardCalculator):
    """Cnezzarandnicebeatmap奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        严格提取最后一个[answer]标签内的答案。
        """
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        if last_match == '-1':
            return [-1]
        try:
            return list(map(int, last_match.split()))
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证排列是否满足所有连续三点角度小于90度。
        """
        if solution == [-1]:
            return False  # 该训练场生成的实例保证有解
        
        n = identity['n']
        points = identity['points']
        if len(solution) != n or set(solution) != set(range(1, n+1)):
            return False
        
        # 检查每个连续三点A,B,C的向量点积
        for i in range(n - 2):
            a, b, c = solution[i], solution[i+1], solution[i+2]
            ax, ay = points[a-1]
            bx, by = points[b-1]
            cx, cy = points[c-1]
            # 向量BA和BC
            ba_x = ax - bx
            ba_y = ay - by
            bc_x = cx - bx
            bc_y = cy - by
            dot_product = ba_x * bc_x + ba_y * bc_y
            if dot_product <= 0:
                return False
        return True
    
    # 其他额外方法

