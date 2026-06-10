import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CarithmeticprogressionRewardCalculator(BaseRewardCalculator):
    """Carithmeticprogression奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        match = re.search(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not match:
            return None
        content = match.group(1).strip()
        
        if content == '-1':
            return -1
        if content == '0':
            return 0
        
        try:
            return sorted(map(int, content.split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['solutions']
    
    # 其他额外方法

