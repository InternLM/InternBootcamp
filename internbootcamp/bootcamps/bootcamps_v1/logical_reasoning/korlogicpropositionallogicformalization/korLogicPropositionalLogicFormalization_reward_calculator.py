import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class KorlogicpropositionallogicformalizationRewardCalculator(BaseRewardCalculator):
    """Korlogicpropositionallogicformalization奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        answers = re.split(r';\s*', last_match)
        return [ans.strip() for ans in answers]
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if identity['type'] != 'symbolize':
            return False
        return all(
            cls.normalize(ans) == cls.normalize(correct)
            for ans, correct in zip(solution, identity['answers'])
        )
    
    # 其他额外方法

