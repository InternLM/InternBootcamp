import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
import math
from collections import deque
from itertools import combinations




class EdigittreeRewardCalculator(BaseRewardCalculator):
    """Edigittree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 强化抽取逻辑，处理多种数字格式
        matches = re.findall(r'\[answer\s*\]\s*(\d+)\s*\[/answer\s*\]', output, re.IGNORECASE)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 添加类型校验
        if not isinstance(solution, int):
            return False
        return solution == identity['expected_answer']
    
    # 其他额外方法

