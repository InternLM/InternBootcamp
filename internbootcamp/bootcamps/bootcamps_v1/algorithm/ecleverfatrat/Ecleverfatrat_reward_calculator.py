import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from typing import Dict
from typing import Any




class EcleverfatratRewardCalculator(BaseRewardCalculator):
    """Ecleverfatrat奖励计算器"""
    
    @staticmethod
    def extract_output(output: str):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        last_answer = matches[-1].strip().lower()
        if last_answer == 'fat rat':
            return 'Fat Rat'
        elif last_answer == 'cerealguy':
            return 'Cerealguy'
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

