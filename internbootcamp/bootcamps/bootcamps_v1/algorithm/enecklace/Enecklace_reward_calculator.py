import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from functools import reduce
from collections import Counter




class EnecklaceRewardCalculator(BaseRewardCalculator):
    """Enecklace奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            lines = solution.split('\n')
            if len(lines) < 2: return False
            k_user = int(lines[0].strip())
            necklace = lines[1].strip().lower()
        except:
            return False

        # Validate bead counts
        if not cls._check_bead_counts(necklace, identity['n'], identity['a']):
            return False

        # Validate palindrome cuts
        valid_k = cls._calculate_max_cuts(identity['n'], identity['a'])
        return k_user == valid_k and valid_k == cls._count_beautiful_cuts(necklace)
    
    # 其他额外方法

