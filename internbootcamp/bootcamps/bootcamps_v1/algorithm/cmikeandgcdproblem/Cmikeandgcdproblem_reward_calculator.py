import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from math import gcd
from functools import reduce




class CmikeandgcdproblemRewardCalculator(BaseRewardCalculator):
    """Cmikeandgcdproblem奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(.*?)\s*\[/answer\]', output, re.DOTALL | re.IGNORECASE)
        if not matches:
            return None
        content = matches[-1].strip().upper()
        lines = [line.strip() for line in content.split('\n')]
        if not lines:
            return None
        if lines[0] == 'YES':
            if len(lines) < 2:
                return None
            try:
                steps = int(lines[1])
                return ('YES', steps)
            except ValueError:
                return None
        elif lines[0] == 'NO':
            return ('NO', None)
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = identity['a']
        current_gcd = reduce(gcd, a)
        
        # 初始gcd>1的验证
        if current_gcd > 1:
            return solution == ('YES', 0)
        
        # 必须通过操作的情况
        cnt = ans = 0
        for x in a:
            if x % 2 == 0:
                ans += (cnt // 2) + 2 * (cnt % 2)
                cnt = 0
            else:
                cnt += 1
        ans += (cnt // 2) + 2 * (cnt % 2)
        return solution == ('YES', ans)
    
    # 其他额外方法

