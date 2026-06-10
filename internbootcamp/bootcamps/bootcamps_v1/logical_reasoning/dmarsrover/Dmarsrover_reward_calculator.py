import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import copy
from collections import deque




class DmarsroverRewardCalculator(BaseRewardCalculator):
    """Dmarsrover奖励计算器"""
    
    @staticmethod
    def extract_output(text):
        matches = re.findall(r'\[answer\]([01]+)\[/answer\]', text)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, sol, case):
        return sol == case['answer']
    
    # 其他额外方法

