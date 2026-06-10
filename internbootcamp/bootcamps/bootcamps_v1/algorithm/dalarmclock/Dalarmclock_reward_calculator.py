import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from bisect import bisect_left
from bisect import bisect_right




class DalarmclockRewardCalculator(BaseRewardCalculator):
    """Dalarmclock奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 严格匹配标签大小写，允许跨行匹配
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        # 处理可能的换行和空格
        last_match = matches[-1].strip().replace('\n', ' ')
        # 合并连续空格
        return ' '.join(last_match.split())
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return int(solution) == identity['ans']
        except (ValueError, TypeError):
            return False
    
    # 其他额外方法

