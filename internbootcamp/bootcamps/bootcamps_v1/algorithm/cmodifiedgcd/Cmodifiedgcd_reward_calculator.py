import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import math
import random




class CmodifiedgcdRewardCalculator(BaseRewardCalculator):
    """Cmodifiedgcd奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
            
        processed = []
        for line in answer_blocks[-1].strip().split('\n'):
            cleaned = line.strip()
            if cleaned:
                try:
                    processed.append(int(cleaned))
                except ValueError:
                    pass
        return processed or None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 双重验证：答案数量必须匹配且每个答案正确
        return (
            isinstance(solution, list) and
            len(solution) == identity['n'] and
            solution == identity['answers']
        )
    
    # 其他额外方法

