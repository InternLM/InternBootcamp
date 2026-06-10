import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import Counter




class DchangingarrayRewardCalculator(BaseRewardCalculator):
    """Dchangingarray奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 使用更鲁棒的正则匹配数字
        matches = re.findall(r'\[answer\][^\d]*(\d+)[^\d]*\[/answer\]', output)
        if not matches:
            return None
        try:
            return int(matches[-1])
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = cls.solve(identity['n'], identity['k'], identity['a'])
        return solution == expected
    
    # 其他额外方法

