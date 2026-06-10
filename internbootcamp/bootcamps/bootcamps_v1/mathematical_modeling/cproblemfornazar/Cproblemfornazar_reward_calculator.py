import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CproblemfornazarRewardCalculator(BaseRewardCalculator):
    """Cproblemfornazar奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(
            r'\[answer\s*\]\s*(\d+)\s*\[\s*/answer\s*\]',  # 允许含空白符
            output, 
            re.IGNORECASE
        )
        if not matches:
            return None
        try:
            last_match = matches[-1]
            # 处理包含分隔符的情况（如1,234,567）
            cleaned = last_match.replace(',', '').replace(' ', '')
            return int(cleaned) % MOD
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 增加调试信息捕获
        try:
            l = identity['l']
            r = identity['r']
            sum_r = cls._calculate_sum(r)
            sum_l_1 = cls._calculate_sum(l-1)
            correct = (sum_r - sum_l_1) % MOD
            return solution % MOD == correct
        except Exception as e:
            print(f"Verification Error: {str(e)}")
            return False
    
    # 其他额外方法

