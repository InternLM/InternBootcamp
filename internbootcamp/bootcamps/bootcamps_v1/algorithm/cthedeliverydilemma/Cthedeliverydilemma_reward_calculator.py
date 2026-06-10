import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re




class CthedeliverydilemmaRewardCalculator(BaseRewardCalculator):
    """Cthedeliverydilemma奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 提取最后一个answer标签内容
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return int(solution) == cls.compute_min_time(
                identity['n'], identity['a'], identity['b']
            )
        except:
            return False
    
    # 其他额外方法

