import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CtwopermutationsRewardCalculator(BaseRewardCalculator):
    """Ctwopermutations奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        numbers = []
        for line in matches[-1].strip().splitlines():
            cleaned = re.sub(r'\D+', '', line)
            if cleaned:
                numbers.append(int(cleaned))
        return numbers if numbers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity.get('answers', [])
    
    # 其他额外方法

