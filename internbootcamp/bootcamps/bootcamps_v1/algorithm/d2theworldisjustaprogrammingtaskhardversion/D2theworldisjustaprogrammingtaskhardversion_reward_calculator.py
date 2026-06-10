import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class D2theworldisjustaprogrammingtaskhardversionRewardCalculator(BaseRewardCalculator):
    """D2theworldisjustaprogrammingtaskhardversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        match = re.search(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not match:
            return None
        content = match.group(1).strip()
        numbers = list(map(int, re.findall(r'\d+', content)))
        if len(numbers) < 3:
            return None
        return (numbers[1], numbers[2])
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        l, r = solution
        n = identity['n']
        s = identity['s']
        s_list = list(s)
        l -= 1
        r -= 1
        s_list[l], s_list[r] = s_list[r], s_list[l]
        new_s = ''.join(s_list)
        beauty = cls.compute_beauty(new_s)
        return beauty == identity['max_beauty']
    
    # 其他额外方法

