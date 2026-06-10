import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class KorpuzzlewordbrainteasersRewardCalculator(BaseRewardCalculator):
    """Korpuzzlewordbrainteasers奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 匹配最后一个有效答案块
        matches = re.findall(r'\[\[([^\]]+)\]\]', output)
        if not matches:
            return None
        last_valid = None
        for m in reversed(matches):
            cleaned = re.sub(r'[^a-zA-Z\s]', '', m).strip()
            if cleaned:
                last_valid = cleaned
                break
        return last_valid.split() if last_valid else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = []
        for pair in identity['components']:
            expected.extend(pair)
        return solution == expected
    
    # 其他额外方法

