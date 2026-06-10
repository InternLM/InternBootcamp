import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CnastyaandawardrobeRewardCalculator(BaseRewardCalculator):
    """Cnastyaandawardrobe奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 多模式匹配（应对不同排版）
        patterns = [
            r'\[answer\](.*?)\[/answer\]',  # 标准格式
            r'answer:\s*(\d+)',             # 兼容无标签格式
            r'最终答案\s*[:：]\s*(\d+)'     # 中文格式
        ]
        for pattern in patterns:
            matches = re.findall(pattern, output, re.DOTALL)
            if matches:
                return matches[-1].strip()
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            x = identity['x']
            k = identity['k']
            
            if x == 0:
                return int(solution) == 0
            
            # 大数安全计算
            mod = cls.MOD
            term = pow(2, k, mod)
            expected = ((2*x - 1) * term + 1) % mod
            return int(solution) == expected
        except:
            return False
    
    # 其他额外方法

