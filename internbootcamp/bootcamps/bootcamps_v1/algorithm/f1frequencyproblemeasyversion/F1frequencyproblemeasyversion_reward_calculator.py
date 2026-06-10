import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import defaultdict
import random
import re




class F1frequencyproblemeasyversionRewardCalculator(BaseRewardCalculator):
    """F1frequencyproblemeasyversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 保持原有抽取逻辑不变
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['answer']
    
    # 其他额外方法

