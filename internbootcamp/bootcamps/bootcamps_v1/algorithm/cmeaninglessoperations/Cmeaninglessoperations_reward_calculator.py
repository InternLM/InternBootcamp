import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CmeaninglessoperationsRewardCalculator(BaseRewardCalculator):
    """Cmeaninglessoperations奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 提取最后一个符合格式的答案
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = identity["a"]
        bit_len = a.bit_length()
        
        # 全1二进制数验证逻辑
        if (a & (a + 1)) == 0:
            # 参考数组索引计算
            correct_index = bit_len - 2
            if 0 <= correct_index < len(cls.n):
                correct = cls.n[correct_index]
            else:
                # 超出数组范围时使用数学公式计算
                correct = (1 << (bit_len - 1)) - 1
        else:
            # 非全1数逻辑
            correct = (1 << bit_len) - 1
        
        try:
            return int(solution) == correct
        except ValueError:
            return False
    
    # 其他额外方法

