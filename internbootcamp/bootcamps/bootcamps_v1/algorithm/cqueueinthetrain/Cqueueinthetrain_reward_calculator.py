import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque
import heapq
import re




class CqueueinthetrainRewardCalculator(BaseRewardCalculator):
    """Cqueueinthetrain奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\][\s\n]*(.*?)[\s\n]*\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            last_answer = matches[-1].strip().replace('\n', ' ')
            return list(map(int, last_answer.split()))
        except (ValueError, AttributeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return solution == identity['correct_output']
        except (KeyError, TypeError):
            return False
    
    # 其他额外方法

