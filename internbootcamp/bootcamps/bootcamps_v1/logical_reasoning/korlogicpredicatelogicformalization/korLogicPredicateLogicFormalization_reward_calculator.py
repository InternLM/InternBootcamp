import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import OrderedDict




class KorlogicpredicatelogicformalizationRewardCalculator(BaseRewardCalculator):
    """Korlogicpredicatelogicformalization奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, flags=re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].replace('\n', ' ').strip()
        return [s.strip() for s in last_match.split(';') if s.strip()]
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            if not isinstance(solution, list) or len(solution) != len(identity["problems"]):
                return False
            return all(
                cls._normalize(sol) == cls._normalize(prob["correct_answer"])
                for sol, prob in zip(solution, identity["problems"])
            )
        except Exception:
            return False
    
    # 其他额外方法

