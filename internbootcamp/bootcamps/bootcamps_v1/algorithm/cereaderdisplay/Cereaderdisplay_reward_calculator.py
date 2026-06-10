import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from typing import List




class CereaderdisplayRewardCalculator(BaseRewardCalculator):
    """Cereaderdisplay奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> int:
        # 增强型匹配模式，处理可能存在的换行符
        matches = re.findall(r'\[answer\s*\]\s*(\d+)\s*\[/\s*answer\s*\]', output, re.IGNORECASE)
        if matches:
            try:
                return int(matches[-1].strip())
            except:
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 双重验证机制
        try:
            # 方法1：预存答案验证
            if solution == identity['correct_answer']:
                return True
            
            # 方法2：实时计算验证（防止逆向生成错误）
            n = identity['n']
            grid = [[int(c) for c in row] for row in identity['grid']]
            calculated = cls.calculate_min_commands(n, grid)
            return solution == calculated
        except:
            return False
    
    # 其他额外方法

