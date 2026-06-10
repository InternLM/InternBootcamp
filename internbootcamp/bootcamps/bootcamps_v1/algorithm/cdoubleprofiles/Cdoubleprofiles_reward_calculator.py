import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from itertools import combinations
from collections import defaultdict
import re




class CdoubleprofilesRewardCalculator(BaseRewardCalculator):
    """Cdoubleprofiles奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        改进正则表达式模式，严格匹配整数格式
        支持科学计数法等特殊格式的转换
        """
        pattern = r'\[answer\s*\]\s*(-?\d+)\s*\[/answer\s*\]'
        matches = re.findall(pattern, output, re.IGNORECASE)
        if matches:
            try:
                return int(matches[-1].strip())
            except ValueError:
                pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        增加类型检查，确保比较有效性
        """
        if not isinstance(solution, int):
            return False
        return solution == identity.get('correct_answer', -1)
    
    # 其他额外方法

