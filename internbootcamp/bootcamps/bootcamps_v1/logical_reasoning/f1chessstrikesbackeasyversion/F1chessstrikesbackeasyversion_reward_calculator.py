import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class F1chessstrikesbackeasyversionRewardCalculator(BaseRewardCalculator):
    """F1chessstrikesbackeasyversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        lines = [line.strip().upper() for line in last_match.split('\n') if line.strip()]
        return lines if lines else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity.get('answers', [])
    
    # 其他额外方法

