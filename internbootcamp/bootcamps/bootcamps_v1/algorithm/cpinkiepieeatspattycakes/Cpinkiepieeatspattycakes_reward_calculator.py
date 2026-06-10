import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class CpinkiepieeatspattycakesRewardCalculator(BaseRewardCalculator):
    """Cpinkiepieeatspattycakes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return answer_blocks[-1].strip() if answer_blocks else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            cnt = defaultdict(int)
            for num in identity['a']:
                cnt[num] += 1
            
            counts = list(cnt.values())
            maxx = max(counts)
            ct = counts.count(maxx)
            
            # 验证题目约束条件
            if maxx < 2 or identity['n'] != len(identity['a']):
                return False
            
            # 根据题目公式计算结果
            expected = (identity['n'] - ct) // (maxx - 1) - 1
            return int(solution) == expected
        except (ValueError, KeyError):
            return False
    
    # 其他额外方法

