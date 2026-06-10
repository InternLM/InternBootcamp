import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class EandreachabilityRewardCalculator(BaseRewardCalculator):
    """Eandreachability奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, flags=re.DOTALL)
        if not matches:
            return None
        answer_block = matches[-1].strip()
        results = []
        for line in answer_block.split('\n'):
            line = line.strip()
            if line in ('Shi', 'Fou'):
                results.append(line)
        return results if results else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answers']
    
    # 其他额外方法

