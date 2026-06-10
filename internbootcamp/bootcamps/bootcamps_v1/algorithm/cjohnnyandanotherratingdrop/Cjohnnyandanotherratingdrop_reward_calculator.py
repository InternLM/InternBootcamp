import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CjohnnyandanotherratingdropRewardCalculator(BaseRewardCalculator):
    """Cjohnnyandanotherratingdrop奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强版数字提取，处理各类异常情况
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        last_match = matches[-1].strip()
        numbers = re.findall(r'-?\d+', last_match.replace(',', ''))  # 处理千分位分隔符
        
        if not numbers:
            return None
        
        try:
            return int(numbers[-1])
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 数学验证逻辑加固
        n = identity["n"]
        if not isinstance(solution, int) or solution < 0:
            return False
        
        correct = 0
        current = n
        while current > 0:
            correct += current
            current >>= 1
        return solution == correct
    
    # 其他额外方法

