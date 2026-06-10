import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EmashmokhandreverseoperationRewardCalculator(BaseRewardCalculator):
    """Emashmokhandreverseoperation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_block = answer_blocks[-1].strip()
        answers = []
        for line in last_block.splitlines():
            stripped = line.strip()
            if stripped:
                try:
                    answers.append(int(stripped))
                except ValueError:
                    pass
        return answers if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity.get('answers', [])
    
    # 其他额外方法

