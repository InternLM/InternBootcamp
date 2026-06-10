import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import defaultdict
import re
import random




class EarpaandagamewithmojtabaRewardCalculator(BaseRewardCalculator):
    """Earpaandagamewithmojtaba奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip().title()
        return last_match if last_match in {"Mojtaba", "Arpa"} else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        
        try:
            # 计算游戏结果的独立模块
            def calculate_sg_total(a):
                prime_states = defaultdict(int)
                for num in a:
                    factors = cls.prime_factors(num)
                    for p, k in factors.items():
                        prime_states[p] |= 1 << (k-1)
                
                sg_total = 0
                for p in prime_states:
                    memo = {}
                    sg_total ^= cls._compute_sg(prime_states[p], memo)
                return sg_total
            
            sg_total = calculate_sg_total(identity['a'])
            expected = "Mojtaba" if sg_total != 0 else "Arpa"
            return solution.strip().lower() == expected.lower()
        
        except Exception:
            return False
    
    # 其他额外方法

