import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class DgeneratingsetsRewardCalculator(BaseRewardCalculator):
    """Dgeneratingsets奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        start = output.rfind('[answer]')
        if start == -1:
            return None
        end = output.find('[/answer]', start)
        if end == -1:
            return None
        content = output[start + len('[answer]'):end].strip()
        if not content:
            return None
        try:
            X = list(map(int, content.split()))
            return X
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        Y = identity['y']
        X = solution
        if len(X) != len(Y):
            return False
        if len(set(X)) != len(X):
            return False
        for y in Y:
            current = y
            found = False
            while current > 0:
                if current in X:
                    found = True
                    break
                if current % 2 == 0:
                    current = current // 2
                else:
                    current = (current - 1) // 2
            if not found:
                return False
        return True
    
    # 其他额外方法

