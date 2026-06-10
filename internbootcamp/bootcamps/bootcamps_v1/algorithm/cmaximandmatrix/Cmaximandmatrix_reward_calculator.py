import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CmaximandmatrixRewardCalculator(BaseRewardCalculator):
    """Cmaximandmatrix奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n_original = identity["n"]
        t_original = identity["t"]
        n_code = n_original + 1
        t = t_original
        tt = 0
        
        # 处理t必须为2的幂次的条件
        while t % 2 == 0 and t != 0:
            t = t // 2
            tt += 1
        if t != 1:
            correct_answer = 0
        else:
            correct_answer = cls.f(n_code, tt)
        
        try:
            user_answer = int(solution)
            return user_answer == correct_answer
        except:
            return False
    
    # 其他额外方法

