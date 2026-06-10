import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class CpermutationgameRewardCalculator(BaseRewardCalculator):
    """Cpermutationgame奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]([A-B]+)\[/answer\]', output, re.IGNORECASE)
        return matches[-1].upper().strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['s']
        return solution == expected if solution else False
    
    # 其他额外方法

