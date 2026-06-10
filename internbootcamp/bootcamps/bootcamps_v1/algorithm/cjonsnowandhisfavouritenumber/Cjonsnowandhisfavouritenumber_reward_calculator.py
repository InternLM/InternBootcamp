import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class CjonsnowandhisfavouritenumberRewardCalculator(BaseRewardCalculator):
    """Cjonsnowandhisfavouritenumber奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output)
        if not matches:
            return None
        try:
            values = list(map(int, matches[-1].strip().split()))
            return (values[0], values[1]) if len(values) == 2 else None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 使用字典优化大n情况的内存占用
        counter = defaultdict(int)
        for s in identity['strengths']:
            counter[s] += 1

        x_val = identity['x']
        for _ in range(identity['k']):
            new_counter = defaultdict(int)
            accumulated = 0
            
            for key in sorted(counter.keys()):
                count = counter[key]
                if not count:
                    continue

                # 计算当前累积总数
                total = accumulated + count
                
                # 需要异或的数量
                xor_count = (total + 1) // 2 - (accumulated + 1) // 2
                new_counter[key ^ x_val] += xor_count
                
                # 普通数量
                new_counter[key] += count - xor_count
                
                accumulated = total

            counter = new_counter

        # 找到最大最小值
        valid_values = [k for k, v in counter.items() if v > 0]
        if not valid_values:
            return False
        return solution == (max(valid_values), min(valid_values))
    
    # 其他额外方法

