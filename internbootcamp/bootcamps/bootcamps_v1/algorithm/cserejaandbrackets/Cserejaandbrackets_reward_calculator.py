import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import math




class CserejaandbracketsRewardCalculator(BaseRewardCalculator):
    """Cserejaandbrackets奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强多格式匹配能力
        pattern = r'(?:<answer>|\[answer\]|答案：?)([\s\d\n]+)(?:<\/answer>|\[\/answer\]|)'
        matches = re.findall(pattern, output, re.IGNORECASE)
        if not matches:
            return None
        
        numbers = []
        for match in matches:
            nums = re.findall(r'\b\d+\b', match)
            numbers.extend(map(int, nums))
        
        # 取最后一个完整答案块
        if numbers and len(numbers) >= len(matches[-1].split()):
            return numbers[-len(matches[-1].split()):]
        return numbers if numbers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity.get('answers', [])
        return isinstance(solution, list) and solution == expected
    
    # 其他额外方法

