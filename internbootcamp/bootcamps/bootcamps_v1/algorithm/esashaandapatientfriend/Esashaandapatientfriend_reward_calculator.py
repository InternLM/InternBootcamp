import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import bisect
from bisect import bisect_left
from bisect import bisect_right




class EsashaandapatientfriendRewardCalculator(BaseRewardCalculator):
    """Esashaandapatientfriend奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip()
        
        # 处理特殊值-1
        if answer.lower() == "-1":
            return -1.0
        
        # 处理科学计数法和浮点格式
        try:
            return float(answer.replace(',', '.'))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity["expected"]
        # 处理-1的情况
        if expected == -1:
            return solution == -1.0
        if solution == -1.0:
            return False
        
        # 计算精度误差
        abs_err = abs(solution - expected)
        rel_err = abs_err / max(1.0, abs(expected))
        return abs_err <= 1e-6 or rel_err <= 1e-6
    
    # 其他额外方法

