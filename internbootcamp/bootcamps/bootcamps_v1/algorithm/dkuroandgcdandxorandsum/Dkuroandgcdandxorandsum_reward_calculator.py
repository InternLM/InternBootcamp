import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import math
import re




class DkuroandgcdandxorandsumRewardCalculator(BaseRewardCalculator):
    """Dkuroandgcdandxorandsum奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        从LLM的回复中提取答案。
        """
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer_str = matches[-1].strip()
        if not answer_str:
            return None
        try:
            return int(answer_str)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证提取的答案是否正确。
        """
        if solution is None:
            return False
        correct_v = identity['correct_v']
        return solution == correct_v
    
    # 其他额外方法

