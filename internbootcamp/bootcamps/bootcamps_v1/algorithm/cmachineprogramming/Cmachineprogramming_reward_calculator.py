import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CmachineprogrammingRewardCalculator(BaseRewardCalculator):
    """Cmachineprogramming奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return list(map(int, last_match.split()))
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 格式验证
        if not solution or len(solution) != identity['n']:
            return False
        if any(bit not in (0,1) for bit in solution):
            return False
        
        # 选择的任务列表
        selected = [t for t, bit in zip(identity['tasks'], solution) if bit]
        
        # 计算实际利润
        actual_profit = sum(t['ci'] for t in selected)
        
        # 验证最优性
        if actual_profit != identity['optimal_profit']:
            return False
        
        # 验证机器约束
        return cls.calculate_overlap(selected, identity['k'])
    
    # 其他额外方法

