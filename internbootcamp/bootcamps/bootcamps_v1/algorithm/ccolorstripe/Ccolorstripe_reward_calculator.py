import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局函数 ===

def solve_min_repaint(n, k, s_str):
    if n == 0:
        return 0, ""
    
    s = list(s_str)
    if k > 2:
        modified = False
        for i in range(1, n):
            if s[i] == s[i-1]:
                available = set(string.ascii_uppercase[:k]) - {s[i-1]}
                if i < n-1:
                    available.discard(s[i+1])
                s[i] = sorted(available)[0]
                modified = True
        
        if modified and s[0] == s[1]:
            available = set(string.ascii_uppercase[:k]) - {s[1]}
            if n >= 3:
                available.discard(s[2])
            s[0] = sorted(available)[0]
        
        cnt = sum(1 for a, b in zip(s, s_str) if a != b)
        return cnt, ''.join(s)
    else:
        pattern1 = ['A' if i%2 ==0 else 'B' for i in range(n)]
        pattern2 = ['B' if i%2 ==0 else 'A' for i in range(n)]
        cnt1 = sum(c != sc for c, sc in zip(pattern1, s))
        cnt2 = sum(c != sc for c, sc in zip(pattern2, s))
        if cnt1 <= cnt2:
            return cnt1, ''.join(pattern1)
        return cnt2, ''.join(pattern2)


class CcolorstripeRewardCalculator(BaseRewardCalculator):
    """Ccolorstripe奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        return '\n'.join(lines[:2]) if len(lines)>=2 else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
            
        try:
            lines = solution.split('\n')
            if len(lines) < 2:
                return False
            reported = int(lines[0].strip())
            result = lines[1].upper().strip()
            
            # 基础验证
            n = identity['n']
            k = identity['k']
            if len(result) != n:
                return False
            if any(c not in string.ascii_uppercase[:k] for c in result):
                return False
            
            # 相邻验证
            for i in range(n-1):
                if result[i] == result[i+1]:
                    return False
            
            # 修改次数验证
            actual = sum(1 for a, b in zip(identity['original_s'], result) if a != b)
            return actual == reported == identity['min_repaints']
        except:
            return False
    
    # 其他额外方法

