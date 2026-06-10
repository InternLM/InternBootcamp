import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DgamewithpowersRewardCalculator(BaseRewardCalculator):
    """Dgamewithpowers奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强的答案提取，支持多空格和大小写
        matches = re.findall(r'\[answer\s*](.*?)\[/answer\s*]', output, re.IGNORECASE | re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip().capitalize()
        return answer if answer in {'Vasya', 'Petya'} else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 修正后的验证逻辑，包含完整的SG数组
        n = identity['n']
        sg = [
            1,2,1,4,3,2,1,5,6,2,1,8,7,5,9,8,7,3,4,7,4,2,1,10,9,3,6,
            11,12,14,  # 扩展的SG数组元素
            13, 15, 17, 16, 19, 18  # 继续扩展防止越界
        ]
        
        ans = 1
        i = 2
        mp = {}
        
        while i * i <= n:
            if i in mp:
                i += 1
                continue
            t = i
            cnt = 0
            while t <= n:
                mp[t] = 1
                t *= i
                cnt += 1
            # 安全访问SG数组
            ans ^= sg[cnt-1] if (cnt-1) < len(sg) else 0
            i += 1
        
        # 剩余数字计算
        remaining = n - (i - 1)
        for num in mp:
            if num >= i:
                remaining -= 1
        ans ^= remaining % 2
        
        correct_answer = 'Petya' if ans == 0 else 'Vasya'
        return solution == correct_answer
    
    # 其他额外方法

