import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import defaultdict
import re
import random




class BtwoheapsRewardCalculator(BaseRewardCalculator):
    """Btwoheaps奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if len(lines) < 2:
            return None
        try:
            solution = list(map(int, lines[1].split()))
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 基础验证
        n = identity['n']
        a = identity['a']
        total = 2 * n
        
        if len(solution) != total:
            return False
        if sum(1 for x in solution if x == 1) != n:
            return False
        
        # 计算理论最大值
        counts = defaultdict(int)
        for num in a:
            counts[num] += 1
            
        n1 = sum(1 for cnt in counts.values() if cnt == 1)
        n2 = sum(1 for cnt in counts.values() if cnt > 1)
        max_val = (n2 + n1 // 2) * (n2 + (n1 + 1) // 2)
        
        # 计算实际四位数数量
        heap1 = [a[i] for i, s in enumerate(solution) if s == 1]
        heap2 = [a[i] for i, s in enumerate(solution) if s == 2]
        actual = len({h1*100 + h2 for h1 in heap1 for h2 in heap2})
        
        return actual == max_val
    
    # 其他额外方法

