import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DandreyandproblemRewardCalculator(BaseRewardCalculator):
    """Dandreyandproblem奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强科学计数法支持
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
            
        try:
            # 处理千分位分隔符和科学计数法
            last_match = matches[-1].strip().replace(',', '')
            if 'e' in last_match or 'E' in last_match:
                return float(f"{float(last_match):.12f}")
            return float(last_match)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            expected = identity['correct_answer']
            return abs(solution - expected) <= 1e-9 + 1e-12  # 增强容错性
        except:
            return False
    
    # 其他额外方法

