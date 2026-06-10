import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CstrangefunctionRewardCalculator(BaseRewardCalculator):
    """Cstrangefunction奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强型数字提取逻辑
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        number_str = re.sub(r'[^0-9]', '', matches[-1].strip())
        try:
            return int(number_str) % (10**9+7) if number_str else None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return solution == cls.compute_answer(identity['n'])
        except:
            return False
    
    # 其他额外方法

