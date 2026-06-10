import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

max_length = 100

max_sum = max_length * 26

dp = [[0] * (max_sum + 1) for _ in range(max_length + 1)]

dp[0][0] = 1


class EcipherRewardCalculator(BaseRewardCalculator):
    """Ecipher奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """强化提取逻辑，处理多种数字格式"""
        matches = re.findall(r'\[answer\][\s]*(-?\d+)[\s]*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """修正验证逻辑"""
        try:
            word = identity['word']
            n = len(word)
            # 合法性检查
            if not (1 <= n <= 100) or not word.islower():
                return False
            
            # 计算字母值总和
            sum_val = sum(ord(c) - ord('a') + 1 for c in word)
            
            # 边界条件保证
            if not (n <= sum_val <= 26*n):
                return solution == 0  # 输入非法时应返回0
            
            # 数据库查询验证
            return (dp[n][sum_val] - 1) % MOD == solution
        except:
            return False
    
    # 其他额外方法

