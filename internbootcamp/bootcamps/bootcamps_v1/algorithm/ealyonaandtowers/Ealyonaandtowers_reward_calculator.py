import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EalyonaandtowersRewardCalculator(BaseRewardCalculator):
    """Ealyonaandtowers奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强格式抽取的容错性
        matches = re.findall(r'\[answer\][\s]*((?:\d+\s*)+)[\s]*\[\/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        try:
            return [int(x) for x in matches[-1].split()]
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 增加类型检查和安全访问
        expected = identity.get('expected_outputs', [])
        if not isinstance(solution, list) or len(solution) != len(expected):
            return False
        return all(s == e for s, e in zip(solution, expected))
    
    # 其他额外方法

