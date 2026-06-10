import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re

# === 源文件中的全局变量 ===

MOD = 998244353


class FslimeandsequenceseasyversionRewardCalculator(BaseRewardCalculator):
    """Fslimeandsequenceseasyversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        last = matches[-1].strip()
        try:
            return list(map(int, last.split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['expected']
        return solution == expected
    
    # 其他额外方法

