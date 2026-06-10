import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class EdatacentermaintenanceRewardCalculator(BaseRewardCalculator):
    """Edatacentermaintenance奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        # 查找所有匹配的答案块并取最后一个
        matches = list(re.finditer(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL))
        if not matches:
            return None
        last_match = matches[-1]
        content = last_match.group(1).strip()
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        
        try:
            if len(lines) < 2:
                return None
            k = int(lines[0])
            centers = list(map(int, lines[1].split()))
            if len(centers) == k and len(set(centers)) == k:
                return centers
        except:
            pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        if not solution:
            return False
            
        h = case['h']
        u = case['u']
        solution_set = set(solution)
        
        for c1, c2 in case['clients']:
            # 计算调整后的时间
            t1 = (u[c1-1] + (1 if c1 in solution_set else 0)) % h
            t2 = (u[c2-1] + (1 if c2 in solution_set else 0)) % h
            if t1 == t2:
                return False
        return True
    
    # 其他额外方法

