import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from functools import reduce
from operator import mul




class CrandomeventsRewardCalculator(BaseRewardCalculator):
    """Crandomevents奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 支持多格式匹配
        patterns = [
            r'\[answer\]\s*(\d+\.\d{6})\s*\[/answer\]',  # 标准格式
            r'answer\s*:\s*(\d+\.\d{6})',               # 无标签格式
            r'\\boxed{(\d+\.\d{6})}'                    # LaTeX格式
        ]
        for pattern in patterns:
            matches = re.findall(pattern, output)
            if matches:
                try:
                    return round(float(matches[-1]), 6)
                except:
                    continue
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        expected = identity['correct_answer']
        
        # 统一使用题目允许的误差标准
        if expected == 0.0:
            return solution < 1e-6  # 允许接近0的值
        elif expected == 1.0:
            return (1.0 - solution) < 1e-6
        
        abs_error = abs(solution - expected)
        rel_error = abs_error / max(1e-6, abs(expected))
        return abs_error < 1e-6 or rel_error < 1e-6
    
    # 其他额外方法

