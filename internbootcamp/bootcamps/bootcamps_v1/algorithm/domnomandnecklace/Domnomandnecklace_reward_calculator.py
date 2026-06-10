import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class DomnomandnecklaceRewardCalculator(BaseRewardCalculator):
    """Domnomandnecklace奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 严格匹配答案格式，允许前后有空格
        matches = re.findall(r'\[answer\s*\]\s*([01]+)\s*\[/?answer\s*\]', output, re.IGNORECASE)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 添加长度校验
        if len(solution) != identity['n']:
            return False
        return solution == identity['correct_output']
    
    # 其他额外方法

