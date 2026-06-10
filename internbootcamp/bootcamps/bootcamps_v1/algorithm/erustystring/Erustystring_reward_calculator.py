import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class ErustystringRewardCalculator(BaseRewardCalculator):
    """Erustystring奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        start = output.rfind('[answer]')
        end = output.rfind('[/answer]')
        if start == -1 or end == -1 or start >= end:
            return None
        
        content = output[start+8:end].strip().split('\n')
        try:
            if len(content) < 2:
                return None
            periods = list(map(int, content[1].strip().split()))
            return periods
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_periods']
    
    # 其他额外方法

