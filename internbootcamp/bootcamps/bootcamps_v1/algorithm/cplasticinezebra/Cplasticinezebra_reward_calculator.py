import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CplasticinezebraRewardCalculator(BaseRewardCalculator):
    """Cplasticinezebra奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 严格匹配整数答案，过滤非数字内容
        answers = re.findall(r'\[answer\s*\](.*?)\[/answer\s*\]', output, re.DOTALL)
        if not answers:
            return None
        try:
            return int(answers[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        s = identity['s']
        return solution == cls._calculate_max_zebra(s)
    
    # 其他额外方法

