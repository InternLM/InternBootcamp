import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class ColdberlandlanguageRewardCalculator(BaseRewardCalculator):
    """Coldberlandlanguage奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if identity['possible']:
            if not solution.startswith("YES"):
                return False
            parts = solution.split('\n')
            if len(parts)-1 != identity['n']:
                return False
            words = parts[1:]
            # 验证长度和前缀条件
            return (
                all(len(w) == l for w, l in zip(words, identity['lengths'])) and
                not any(w1.startswith(w2) or w2.startswith(w1) 
                        for i, w1 in enumerate(words) 
                        for j, w2 in enumerate(words) if i != j)
            )
        else:
            return solution.strip().upper() == 'NO'
    
    # 其他额外方法

