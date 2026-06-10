import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EmuseumstourRewardCalculator(BaseRewardCalculator):
    """Emuseumstour奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强答案提取鲁棒性"""
        matches = re.findall(r'\[answer\s*\](.*?)\[/answer\s*\]', output, re.DOTALL|re.IGNORECASE)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """直接比对预计算结果"""
        return solution == identity['correct_answer']
    
    # 其他额外方法

