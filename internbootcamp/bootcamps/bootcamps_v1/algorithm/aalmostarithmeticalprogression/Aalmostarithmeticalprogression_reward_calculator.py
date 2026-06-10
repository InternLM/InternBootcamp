import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict




class AalmostarithmeticalprogressionRewardCalculator(BaseRewardCalculator):
    """Aalmostarithmeticalprogression奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip().split()[0].replace(',', ''))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not isinstance(solution, int) or solution < 1:
            return False
        return solution == identity["ans"]
    
    # 其他额外方法

