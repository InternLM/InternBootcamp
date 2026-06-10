import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import random




class ComnomandcandiesRewardCalculator(BaseRewardCalculator):
    """Comnomandcandies奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 查找最后一个[answer]标签内的内容
        start = output.rfind('[answer]')
        if start == -1:
            return None
        end = output.find('[/answer]', start)
        if end == -1:
            return None
        answer_str = output[start + 8:end].strip()
        try:
            return int(answer_str)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 比较提取的答案与正确解
        if solution is None:
            return False
        return solution == identity['correct_joy']
    
    # 其他额外方法

