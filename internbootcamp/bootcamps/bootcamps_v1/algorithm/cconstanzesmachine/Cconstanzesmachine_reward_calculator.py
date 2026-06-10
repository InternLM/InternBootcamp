import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

MAX_FIB_LENGTH = 10**5 + 10  # 覆盖题目最大输入长度


class CconstanzesmachineRewardCalculator(BaseRewardCalculator):
    """Cconstanzesmachine奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output, re.DOTALL)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 直接计算结果进行验证
            s = identity['s']
            if 'm' in s or 'w' in s:
                return int(solution) == 0
            
            result = 1
            i = 0
            n = len(s)
            while i < n:
                if s[i] not in ('u', 'n'):
                    i += 1
                    continue
                
                j = i
                while j < n and s[j] == s[i]:
                    j += 1
                
                block_len = j - i
                if block_len >= 1:
                    result = (result * cls.fib[block_len]) % MOD
                i = j
            
            expected = result % MOD
            return int(solution) == expected
        except:
            return False
    
    # 其他额外方法

