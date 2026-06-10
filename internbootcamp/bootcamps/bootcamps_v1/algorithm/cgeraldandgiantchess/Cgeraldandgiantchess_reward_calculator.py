import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CgeraldandgiantchessRewardCalculator(BaseRewardCalculator):
    """Cgeraldandgiantchess奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 解析输入参数
            h = identity['h']
            w = identity['w']
            blocks = [(r, c) for r, c in identity['black_cells']]
            target = (h, w)
            
            # 包含终点并排序障碍点
            points = sorted(blocks + [target], key=lambda p: (p[0], p[1]))
            
            # 动态计算组合数
            max_n = h + w
            fact = [1]*(max_n+1)
            for i in range(1, max_n+1):
                fact[i] = fact[i-1] * i % MOD
                
            inv_fact = [1]*(max_n+1)
            inv_fact[max_n] = pow(fact[max_n], MOD-2, MOD)
            for i in range(max_n-1, -1, -1):
                inv_fact[i] = inv_fact[i+1] * (i+1) % MOD
            
            def comb(n, k):
                if n < 0 or k < 0 or n < k:
                    return 0
                return fact[n] * inv_fact[k] % MOD * inv_fact[n-k] % MOD
            
            # 递推计算路径数
            dp = []
            for i, (x, y) in enumerate(points):
                # 到当前点的总路径数
                total = comb(x+y-2, x-1)
                
                # 减去经过前面障碍点的路径
                for j in range(i):
                    px, py = points[j]
                    if px <= x and py <= y:
                        dx = x - px
                        dy = y - py
                        subtract = dp[j] * comb(dx + dy, dx) % MOD
                        total = (total - subtract) % MOD
                
                dp.append(total)
            
            expected = dp[-1] % MOD
            actual = int(solution.strip()) % MOD
            return actual == expected
        except:
            return False
    
    # 其他额外方法

