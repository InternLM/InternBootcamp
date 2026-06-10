import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CmainsequenceRewardCalculator(BaseRewardCalculator):
    """Cmainsequence奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        return matches[-1].strip()
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # Handle empty solution
        lines = [l.strip() for l in solution.split('\n') if l.strip()]
        if not lines:
            return False

        # Check NO case
        if lines[0].upper() == 'NO':
            # Verify using reference algorithm
            try:
                n = identity['n']
                p = list(identity['p'])
                q_list = list(identity['q'])
                
                # Apply q modifications
                for pos in q_list:
                    if 1 <= pos <= n:
                        p[pos-1] *= -1
                
                # Run reference validation
                stack = []
                for i in reversed(range(n)):
                    val = abs(p[i])
                    if stack and stack[-1] == val:
                        stack.pop()
                    else:
                        stack.append(val)
                        p[i] = -val
                
                return len(stack) != 0
            except:
                return False

        # Check YES case
        if len(lines) < 2 or lines[0].upper() != 'YES':
            return False

        try:
            x = list(map(int, lines[1].split()))
        except:
            return False

        # Basic validation
        if len(x) != identity['n']:
            return False
        
        # Check p matching
        for xi, pi in zip(x, identity['p']):
            if abs(xi) != pi:
                return False
        
        # Check q positions
        q_set = set(identity['q'])
        for i in range(len(x)):
            pos = i + 1
            if pos in q_set:
                if x[i] >= 0:
                    return False
            else:
                if x[i] <= 0:
                    return False
        
        # Validate bracket sequence
        stack = []
        for num in x:
            if num > 0:
                stack.append(num)
            else:
                if not stack or stack[-1] != -num:
                    return False
                stack.pop()
        
        return not stack
    
    # 其他额外方法

