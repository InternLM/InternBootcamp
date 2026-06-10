import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CservalandparenthesissequenceRewardCalculator(BaseRewardCalculator):
    """Cservalandparenthesissequence奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if matches:
            last_match = matches[-1].strip()
            return last_match if last_match else None
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        s = identity['s']
        n = identity['n']
        # 处理无解情况
        if solution == ':(':
            return cls.solve_parenthesis(s) == ':('
        # 格式检查
        if len(solution) != n:
            return False
        # 原始字符串固定位置检查
        for i in range(n):
            if s[i] != '?' and solution[i] != s[i]:
                return False
        # 整体有效性检查
        if not cls.is_valid_parenthesis(solution):
            return False
        # 严格前缀检查
        for l in range(1, n):
            if cls.is_valid_parenthesis(solution[:l]):
                return False
        return True
    
    # 其他额外方法

