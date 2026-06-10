import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class Dchallengesinschool41RewardCalculator(BaseRewardCalculator):
    """Dchallengesinschool41奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 提取最后一个answer块并验证格式
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
            
        content = matches[-1].strip()
        steps = []
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 1:
                continue
            try:
                parts = list(map(int, parts))
                n_i = parts[0]
                if n_i != len(parts[1:]) or any(p <=0 for p in parts[1:]):
                    continue
                # 检查是否升序排列且不重复
                sorted_p = sorted(parts[1:])
                if sorted_p != parts[1:] or len(set(sorted_p)) != len(sorted_p):
                    continue
                steps.append(sorted_p)
            except:
                continue
        return steps if steps else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        k = identity['k']
        initial = list(identity['initial'])
        
        if len(solution) != k:
            return False
        
        current_state = initial.copy()
        for step in solution:
            # 检查步骤格式
            if not step or any(p <1 or p >=n for p in step):
                return False
            # 检查升序且不重复不连续
            prev = -1
            for p in step:
                if p <= prev or p - prev == 1:
                    return False
                prev = p
            # 验证RL对存在
            temp_state = current_state.copy()
            for p in step:
                idx = p-1
                if idx >= len(temp_state)-1 or temp_state[idx] != 'R' or temp_state[idx+1] != 'L':
                    return False
                temp_state[idx] = 'L'
                temp_state[idx+1] = 'R'
            current_state = temp_state
        
        # 检查最终状态
        return not any(current_state[i] == 'R' and current_state[i+1] == 'L' for i in range(n-1))
    
    # 其他额外方法

