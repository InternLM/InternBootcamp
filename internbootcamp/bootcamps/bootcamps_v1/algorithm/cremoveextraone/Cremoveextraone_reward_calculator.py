import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import bisect




class CremoveextraoneRewardCalculator(BaseRewardCalculator):
    """Cremoveextraone奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        Extract the last occurrence of an answer between [answer] tags.
        """
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        Verify if extracted solution matches precomputed answer.
        """
        return solution == identity['answer']
    
    # 其他额外方法

