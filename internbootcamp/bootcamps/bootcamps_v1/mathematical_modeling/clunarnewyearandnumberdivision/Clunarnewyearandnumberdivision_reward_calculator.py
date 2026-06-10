import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class ClunarnewyearandnumberdivisionRewardCalculator(BaseRewardCalculator):
    """Clunarnewyearandnumberdivision奖励计算器"""
    
    @staticmethod
    def extract_output(text):
        """增强答案提取"""
        answers = re.findall(r'\[answer\]([\d,]+)\[/answer\]', text.replace(',', ''))
        return int(answers[-1]) if answers else None
    
    @classmethod
    def _verify_correction(cls, ans, case):
        """精确校验"""
        return ans == case['correct']
    
    # 其他额外方法

