import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random




class CshootinggalleryRewardCalculator(BaseRewardCalculator):
    """Cshootinggallery奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        
        try:
            # 处理科学计数法和多余空格
            value_str = matches[-1].strip().replace(' ', '').lower()
            if 'e' in value_str:
                return round(float(value_str), 10)
            return float(value_str)
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        expected = identity['correct_answer']
        return abs(solution - expected) <= 1e-6 + 1e-10  # 双精度容差
    
    # 其他额外方法

