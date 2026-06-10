import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EgreedyshoppingRewardCalculator(BaseRewardCalculator):
    """Egreedyshopping奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\][\s]*((?:\d+\s*)+)[\s]*\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        numbers = re.findall(r'\d+', matches[-1])
        return [int(num) for num in numbers] if numbers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity.get('answers', [])
    
    # 其他额外方法

