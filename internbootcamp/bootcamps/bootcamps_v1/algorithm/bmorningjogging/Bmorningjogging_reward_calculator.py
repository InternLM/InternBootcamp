import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import re




class BmorningjoggingRewardCalculator(BaseRewardCalculator):
    """Bmorningjogging奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer_block = matches[-1].strip()
        solution = []
        for line in answer_block.split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                nums = list(map(int, line.split()))
                solution.append(nums)
            except:
                continue
        return solution if len(solution) > 0 else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['n']
            m = identity['m']
            segments = identity['segments']
            correct_sum = identity['correct_sum']
            
            # 验证格式
            if len(solution) != n:
                return False
            for i in range(n):
                if sorted(solution[i]) != sorted(segments[i]):
                    return False
            
            # 计算实际和
            runner_mins = [min(solution[i][j] for i in range(n)) for j in range(m)]
            return sum(runner_mins) == correct_sum
            
        except Exception as e:
            return False
    
    # 其他额外方法

