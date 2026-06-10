import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class DmahmoudandehabandanotherarrayconstructiontaskRewardCalculator(BaseRewardCalculator):
    """Dmahmoudandehabandanotherarrayconstructiontask奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        try:
            return list(map(int, last_answer.split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected_b = identity.get('expected_b', [])
        return solution == expected_b
    
    # 其他额外方法

