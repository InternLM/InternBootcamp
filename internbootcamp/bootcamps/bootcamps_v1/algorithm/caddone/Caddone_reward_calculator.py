import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CaddoneRewardCalculator(BaseRewardCalculator):
    """Caddone奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 支持多空格和换行的健壮正则
        pattern = r'\[answer\][\s\n]*(\d+)[\s\n]*\[/answer\]'
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        cls._precompute_mmap()
        n, m = identity['n'], identity['m']
        
        # 处理n=0的特殊情况（虽然题目限制n≥1）
        if n == 0:
            return solution == 1 if m == 0 else 0
        
        total = 0
        while n > 0:
            d = n % 10
            k = m + d
            if k < len(cls._mmap):
                total = (total + cls._mmap[k]) % cls.MOD
            else:
                # 动态计算超出预处理范围的情况（理论上不应发生）
                pass  
            n //= 10
        return total == solution
    
    # 其他额外方法

