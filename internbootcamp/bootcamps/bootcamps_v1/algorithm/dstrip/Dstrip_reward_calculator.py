import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from math import inf

# === 源文件中的全局函数 ===

def _test():
    bootcamp = Dstripbootcamp(ensure_solvable=True)
    case = bootcamp.case_generator()
    print("Generated case:", case)
    print("Prompt:\n", bootcamp.prompt_func(case))
    
    # 测试解法
    assert bootcamp._verify_correction(case['correct_answer'], case), "Validation failed"


class DstripRewardCalculator(BaseRewardCalculator):
    """Dstrip奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 严格匹配最终答案
        matches = re.findall(
            r'\[answer\][\s]*(-?\d+)[\s]*\[/answer\]', 
            output, 
            flags=re.IGNORECASE
        )
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 动态验证算法
        n, s, l, a = identity['n'], identity['s'], identity['l'], identity['a']
        
        # 边界条件检查
        if solution == -1:
            # 验证确实无解
            dp = [inf]*(n+1)
            dp[0] = 0
            for i in range(1, n+1):
                for j in range(max(0, i-3*l), i-l+1):
                    if j < 0: continue
                    seg = a[j:i]
                    if max(seg)-min(seg) <= s:
                        dp[i] = min(dp[i], dp[j]+1)
            return dp[n] == inf
        
        # 正向验证
        current_pos = 0
        pieces = []
        while current_pos < n:
            found = False
            for end in range(min(n, current_pos+l), n+1):
                seg = a[current_pos:end]
                if len(seg) >= l and max(seg)-min(seg) <= s:
                    pieces.append(seg)
                    current_pos = end
                    found = True
                    break
            if not found:
                return False
        return len(pieces) == solution
    
    # 其他额外方法

