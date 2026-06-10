import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from heapq import heapify
from heapq import heappop
from heapq import heappush
import re




class CphoenixandtowersRewardCalculator(BaseRewardCalculator):
    """Cphoenixandtowers奖励计算器"""
    
    @staticmethod
    def extract_output(text):
        """精确答案提取"""
        answer_blocks = re.findall(
            r'\[answer\](.*?)\[/answer\]', 
            text, 
            re.DOTALL
        )
        
        if not answer_blocks:
            return None
            
        last_answer = answer_blocks[-1].strip()
        lines = [l.strip() for l in last_answer.split('\n') if l.strip()]
        
        if not lines:
            return None
            
        if lines[0].upper() == 'NO':
            return 'NO'
            
        if len(lines) > 1 and lines[0].upper() == 'YES':
            try:
                return list(map(int, lines[1].split()))
            except ValueError:
                pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        """严格答案验证"""
        # 所有生成案例都有解，NO回答直接判错
        if isinstance(solution, str) or solution == 'NO':
            return False
            
        n, m, x = case['n'], case['m'], case['x']
        blocks = case['blocks']
        
        # 基本格式检查
        if len(solution) != n:
            return False
        if any(not (1 <= y <= m) for y in solution):
            return False
            
        # 检查每个塔至少一个块
        towers = set(solution)
        if len(towers) != m:
            return False
            
        # 计算各塔高度
        height = [0] * (m+1)  # 1-based索引
        for h, y in zip(blocks, solution):
            height[y] += h
            
        # 检查高度差
        existing_heights = [h for h in height[1:] if h > 0]
        return max(existing_heights) - min(existing_heights) <= x
    
    # 其他额外方法

