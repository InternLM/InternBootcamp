import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class EicecreamcoloringRewardCalculator(BaseRewardCalculator):
    """Eicecreamcoloring奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[\/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        lines = last_answer.split('\n')
        if len(lines) < 2:
            return None
        try:
            c = int(lines[0].strip())
            colors = list(map(int, lines[1].strip().split()))
            return (c, colors)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        c, colors = solution
        if len(colors) != identity['m']:
            return False
        if any(color < 1 or color > c for color in colors):
            return False
        for u, v in identity['g_edges']:
            if colors[u-1] == colors[v-1]:
                return False
        return True
    
    # 其他额外方法

