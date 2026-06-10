import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class KorpuzzlewordrootsandaffixesRewardCalculator(BaseRewardCalculator):
    """Korpuzzlewordrootsandaffixes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution.strip().lower() == identity['affix'].lower()
    
    # 其他额外方法

