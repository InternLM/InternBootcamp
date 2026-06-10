import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class EchoosingballsRewardCalculator(BaseRewardCalculator):
    """Echoosingballs奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answers = []
        for line in matches[-1].strip().split('\n'):
            line = line.strip()
            if line:
                try:
                    answers.append(int(line))
                except:
                    continue
        return answers if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['expected_outputs']
        return isinstance(solution, list) and len(solution) == len(expected) and all(s == e for s, e in zip(solution, expected))
    
    # 其他额外方法

