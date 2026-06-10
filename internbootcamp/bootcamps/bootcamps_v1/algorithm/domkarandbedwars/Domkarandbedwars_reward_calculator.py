import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from itertools import groupby
import re




class DomkarandbedwarsRewardCalculator(BaseRewardCalculator):
    """Domkarandbedwars奖励计算器"""
    
    @staticmethod
    def extract_output(text: str):
        """严格提取最后一个答案标签内容"""
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', text, re.IGNORECASE)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """直接比对预计算答案"""
        return solution == identity['correct_answer']
    
    # 其他额外方法

