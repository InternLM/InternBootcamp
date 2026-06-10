import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CbadsequenceRewardCalculator(BaseRewardCalculator):
    """Cbadsequence奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        从LLM的回复中提取答案
        """
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if matches:
            return matches[-1].strip().lower()
        else:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证答案是否正确
        """
        s = identity['s']
        n = identity['n']
        
        # 括号数量不平衡，直接返回False
        left = s.count('(')
        right = s.count(')')
        if left != right:
            return False
        
        # 计算需要调整的最少移动次数
        current_depth = 0
        required_moves = 0
        max_depth = 0
        
        for char in s:
            if char == '(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            else:
                current_depth -= 1
                if current_depth < 0:
                    # 需要一个移动来纠正这种情况
                    required_moves += 1
                    # 假设我们移动了一个括号，深度回到0
                    current_depth = 0
        
        # 最大深度超过1的情况需要额外的移动次数
        if max_depth > 1:
            required_moves += 1
        
        # 是否可以通过最多一次移动解决
        expected = "Yes" if required_moves <= 1 else "No"
        return solution.lower() == expected.lower()
    
    # 其他额外方法

