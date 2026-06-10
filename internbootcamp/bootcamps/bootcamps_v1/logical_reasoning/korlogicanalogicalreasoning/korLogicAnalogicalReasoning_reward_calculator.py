import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class KorlogicanalogicalreasoningRewardCalculator(BaseRewardCalculator):
    """Korlogicanalogicalreasoning奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[\[([AB])\]\]', output)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        return solution == case['correct_answer']
    
    # 其他额外方法

