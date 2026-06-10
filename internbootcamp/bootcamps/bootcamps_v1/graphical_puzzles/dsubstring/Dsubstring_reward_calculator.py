import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque
from collections import defaultdict




class DsubstringRewardCalculator(BaseRewardCalculator):
    """Dsubstring奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        start = output.rfind('[answer]')
        if start == -1:
            return None
        end = output.find('[/answer]', start)
        if end == -1:
            return None
        answer_str = output[start+8:end].strip()
        if not answer_str:
            return None
        try:
            return int(answer_str)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        correct_answer = identity['correct_answer']
        if solution is None:
            return False
        return solution == correct_answer
    
    # 其他额外方法

