import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CpocketbookRewardCalculator(BaseRewardCalculator):
    """Cpocketbook奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        product = 1
        mod = 10**9 + 7
        
        # 动态计算每列实际的不同字符数
        names = identity['names']
        m = identity['m']
        for k in range(m):
            column_chars = set(name[k] for name in names)
            product = (product * len(column_chars)) % mod
        
        return solution == product
    
    # 其他额外方法

