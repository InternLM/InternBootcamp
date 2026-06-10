import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class BtaxesRewardCalculator(BaseRewardCalculator):
    """Btaxes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE)
        if matches:
            try:
                return int(matches[-1].strip())
            except (ValueError, TypeError):
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity.get('correct_answer')
    
    # 其他额外方法

