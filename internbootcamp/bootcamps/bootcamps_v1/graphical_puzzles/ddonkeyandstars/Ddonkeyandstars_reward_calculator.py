import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from bisect import bisect_left
import re
import random
import math




class DdonkeyandstarsRewardCalculator(BaseRewardCalculator):
    """Ddonkeyandstars奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        try:
            # 直接从case参数获取验证参数
            a, b, c, d = identity['_params']
            stars = identity['stars_coordinates']
            
            # 执行参考算法
            transformed = []
            for x, y in stars:
                tx = c * x - d * y
                ty = b * y - a * x
                if tx > 0 and ty > 0:
                    transformed.append((tx, -ty))
            
            transformed.sort()
            lis = []
            for x, y in transformed:
                idx = bisect_left(lis, y)
                if idx == len(lis):
                    lis.append(y)
                else:
                    lis[idx] = y
            return solution == len(lis)
        except:
            return False
    
    # 其他额外方法

