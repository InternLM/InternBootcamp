import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re




class BsashaandonemorenameRewardCalculator(BaseRewardCalculator):
    """Bsashaandonemorename奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL|re.IGNORECASE)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        s = identity['s']
        solution = str(solution).strip().lower()
        
        # Impossible条件判断
        if len(set(s)) == 1:
            return solution == "impossible"
        
        # 检查是否存在k=1的解
        has_k1_solution = any(cls._is_valid_rotation(s, i) for i in range(1, len(s)))
        
        # 正确答案逻辑
        if has_k1_solution:
            return solution == "1"
        else:
            # 当原始字符串为双字符回文时特殊处理（如aa）
            return solution in ("2", "impossible") if len(s) == 2 else solution == "2"
    
    # 其他额外方法

