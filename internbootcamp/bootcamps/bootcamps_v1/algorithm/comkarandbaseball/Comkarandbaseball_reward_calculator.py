import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class ComkarandbaseballRewardCalculator(BaseRewardCalculator):
    """Comkarandbaseball奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 逆向搜索最后一个答案标签对
        end_pos = output.rfind('[/answer]')
        if end_pos == -1:
            return None
        start_pos = output.rfind('[answer]', 0, end_pos)
        if start_pos == -1:
            return None
        return output[start_pos+8:end_pos].strip()
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return int(solution) == identity['answer']
        except (ValueError, KeyError):
            return False
    
    # 其他额外方法

