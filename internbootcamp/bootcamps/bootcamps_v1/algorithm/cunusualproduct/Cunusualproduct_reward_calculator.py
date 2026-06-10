import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CunusualproductRewardCalculator(BaseRewardCalculator):
    """Cunusualproduct奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 正确计算初始对角线异或和
        initial_S = sum(row[i] for i, row in enumerate(identity['matrix'])) % 2
        flip_count = 0
        
        expected = []
        for query in identity['queries']:
            if query['type'] == 3:
                expected.append(str((initial_S + flip_count) % 2))
            else:
                flip_count += 1
        return solution == ''.join(expected)
    
    # 其他额外方法

