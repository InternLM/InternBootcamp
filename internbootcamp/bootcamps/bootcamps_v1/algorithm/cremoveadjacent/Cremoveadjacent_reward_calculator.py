import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re




class CremoveadjacentRewardCalculator(BaseRewardCalculator):
    """Cremoveadjacent奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """严格提取最后一个[answer]标签内容"""
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """严格验证答案的正確性"""
        return solution == cls.compute_max_removals(identity['s'])
    
    # 其他额外方法

