import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re




class CnamingcompanyRewardCalculator(BaseRewardCalculator):
    """Cnamingcompany奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强答案提取鲁棒性"""
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        """严格验证答案正确性"""
        expected = cls._calculate_answer(case['s'], case['t'])
        return solution == expected
    
    # 其他额外方法

