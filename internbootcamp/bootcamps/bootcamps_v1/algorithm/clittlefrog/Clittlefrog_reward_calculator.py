import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class ClittlefrogRewardCalculator(BaseRewardCalculator):
    """Clittlefrog奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = list(map(int, last_match.split()))
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        # 检查长度是否正确
        if len(solution) != n:
            return False
        # 检查是否是1到n的排列
        if sorted(solution) != list(range(1, n+1)):
            return False
        # 检查相邻差是否互不相同
        diffs = []
        for i in range(n-1):
            diff = abs(solution[i] - solution[i+1])
            if diff in diffs:
                return False
            diffs.append(diff)
        return True
    
    # 其他额外方法

