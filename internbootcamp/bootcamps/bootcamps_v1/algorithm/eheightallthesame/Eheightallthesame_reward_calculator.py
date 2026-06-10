import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EheightallthesameRewardCalculator(BaseRewardCalculator):
    """Eheightallthesame奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强模式：允许数字前后有非数字字符
        matches = re.findall(
            r'\[answer\D*?(\d+)\D*?\[/answer\]', 
            output, 
            flags=re.IGNORECASE|re.DOTALL
        )
        return int(matches[-1]) % 998244353 if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        MOD = 998244353
        n, m, L, R = identity.values()
        k = n * m
        
        # 计算有效解数量的核心算法
        if k % 2 == 1:
            return solution == pow(R - L + 1, k, MOD)
        else:
            cnt = R - L + 1
            half = cnt // 2
            even_choices = half + (cnt % 2)  # 偶数元素个数
            odd_choices = half               # 奇数元素个数
            return solution == (
                (pow(even_choices + odd_choices, k, MOD) + 
                 pow(even_choices - odd_choices, k, MOD)) 
                * 499122177 % MOD  # 乘以模逆元2^-1 mod 998244353
            )
    
    # 其他额外方法

