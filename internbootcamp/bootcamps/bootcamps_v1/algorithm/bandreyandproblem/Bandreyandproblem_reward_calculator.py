import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class BandreyandproblemRewardCalculator(BaseRewardCalculator):
    """Bandreyandproblem奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            # 处理科学计数法和多余字符
            cleaned = last_match.strip().rstrip('.').replace(',', '')
            return float(cleaned)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        try:
            sol = float(solution)
            expected = identity["expected"]
            return abs(sol - expected) <= 1e-9
        except:
            return False
    
    # 其他额外方法

