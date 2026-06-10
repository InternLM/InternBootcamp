import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class DjonandorbsRewardCalculator(BaseRewardCalculator):
    """Djonandorbs奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        answer_blocks = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_block = answer_blocks[-1].strip()
        answers = []
        for line in last_block.split('\n'):
            line = line.strip()
            if line:
                try:
                    answers.append(int(line))
                except ValueError:
                    pass
        return answers if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity.get('answers', [])
        if not solution or len(solution) != len(expected):
            return False
        return all(s == e for s, e in zip(solution, expected))
    
    # 其他额外方法

