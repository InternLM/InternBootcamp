import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class BcountpairsRewardCalculator(BaseRewardCalculator):
    """Bcountpairs奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 匹配所有可能的答案块，提取最后一个的数字部分
        matches = re.findall(r'\[answer\][^\d]*(\d+)[^\d]*\[/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['ans']
    
    # 其他额外方法

