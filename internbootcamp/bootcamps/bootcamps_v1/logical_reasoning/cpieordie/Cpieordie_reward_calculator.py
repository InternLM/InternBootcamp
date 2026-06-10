import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CpieordieRewardCalculator(BaseRewardCalculator):
    """Cpieordie奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE | re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip().upper()
        return last_match if last_match in ['YES', 'NO'] else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity.get('answer', 'NO')
    
    # 其他额外方法

