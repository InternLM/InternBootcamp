import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from itertools import combinations




class CbugincodeRewardCalculator(BaseRewardCalculator):
    """Cbugincode奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip().split()[-1])  # 提取最后一个答案的数字部分
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['n']
            p = identity['p']
            pairs = identity['pairs']
            
            # 使用字典加速查找
            accusation_map = {i: set(pair) for i, pair in enumerate(pairs, 1)}
            
            valid_pairs = 0
            for u, v in combinations(range(1, n+1), 2):
                count = 0
                for acc in accusation_map.values():
                    if u in acc or v in acc:
                        count += 1
                        if count >= p:  # 提前终止
                            break
                if count >= p:
                    valid_pairs += 1
            return int(solution) == valid_pairs
        except Exception as e:
            print(f"Verification error: {e}")
            return False
    
    # 其他额外方法

