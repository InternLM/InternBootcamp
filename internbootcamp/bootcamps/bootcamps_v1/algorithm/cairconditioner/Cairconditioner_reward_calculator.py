import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict




class CairconditionerRewardCalculator(BaseRewardCalculator):
    """Cairconditioner奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        answer = matches[-1].strip().upper()
        return answer if answer in {'YES', 'NO'} else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = cls._solve_identity(identity)
        return solution.upper() == expected
    
    # 其他额外方法

