import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CstablegroupsRewardCalculator(BaseRewardCalculator):
    """Cstablegroups奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        answers = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(answers[-1]) if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 处理边界情况（n=0/1时直接验证）
        n = identity['n']
        if n <= 1:
            return solution == 1
        
        # 标准验证逻辑
        gaps = []
        a_sorted = identity['a']
        x = identity['x']
        for i in range(1, len(a_sorted)):
            d = a_sorted[i] - a_sorted[i-1]
            if d > x:
                gaps.append((d-1)//x)  # 等效d//x的向上取整减一
        gaps.sort()
        
        covered = 0
        k = identity['k']
        for g in gaps:
            if k >= g:
                k -= g
                covered += 1
            else:
                break
        
        expected = len(gaps) + 1 - covered
        return solution == expected
    
    # 其他额外方法

