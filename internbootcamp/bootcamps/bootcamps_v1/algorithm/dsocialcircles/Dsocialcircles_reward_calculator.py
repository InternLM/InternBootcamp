import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DsocialcirclesRewardCalculator(BaseRewardCalculator):
    """Dsocialcircles奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 支持多种数字格式（包含逗号、空格、汉字数字）
        pattern = r'\[answer\][\s*]*([+-]?[\d, ]+)(?:\[/answer\]|$)'
        matches = re.findall(pattern, output, re.IGNORECASE)
        if not matches:
            return None
        
        try:
            last_match = matches[-1].replace(',', '').replace(' ', '')
            # 处理中文数字
            if '万' in last_match:
                return int(float(last_match.replace('万', '')) * 10000)
            return int(last_match)
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            if not isinstance(solution, int):
                sol = int(str(solution).strip())
            else:
                sol = solution
            
            guests = identity['guests']
            l_sorted = sorted(li for li, ri in guests)
            r_sorted = sorted(ri for li, ri in guests)
            correct = sum(max(l, r) + 1 for l, r in zip(l_sorted, r_sorted))
            return sol == correct
        except:
            return False
    
    # 其他额外方法

