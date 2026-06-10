import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DstasandthequeueatthebuffetRewardCalculator(BaseRewardCalculator):
    """Dstasandthequeueatthebuffet奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        try:
            return int(last_answer)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['n']
            students = identity['students']
            # 不论输入顺序，按正确规则排序验证
            sorted_students = sorted(students, key=lambda s: (s[1] - s[0]))
            total = sum(i * s[0] + (n - i - 1) * s[1] for i, s in enumerate(sorted_students))
            return solution == total
        except:
            return False
    
    # 其他额外方法

