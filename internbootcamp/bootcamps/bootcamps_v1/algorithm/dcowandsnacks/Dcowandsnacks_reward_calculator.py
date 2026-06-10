import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DcowandsnacksRewardCalculator(BaseRewardCalculator):
    """Dcowandsnacks奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强异常处理
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL | re.IGNORECASE)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 直接调用计算函数验证
            return int(solution) == cls._compute_min_sad(
                identity['n'],
                identity['k'],
                identity['guests']
            )
        except:
            return False
    
    # 其他额外方法

