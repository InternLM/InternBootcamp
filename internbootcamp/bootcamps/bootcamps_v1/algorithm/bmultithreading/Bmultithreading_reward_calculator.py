import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class BmultithreadingRewardCalculator(BaseRewardCalculator):
    """Bmultithreading奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强鲁棒性的答案提取"""
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output, re.IGNORECASE)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """严格遵循参考代码逻辑的验证"""
        a = identity['a'][::-1]  # 此处进行正确的数组方向处理
        pre_min, count = len(a) + 1, 0
        
        for num in a:
            if num < pre_min:
                pre_min = num
                count += 1
            else:
                break
        return solution == (len(a) - count)
    
    # 其他额外方法

