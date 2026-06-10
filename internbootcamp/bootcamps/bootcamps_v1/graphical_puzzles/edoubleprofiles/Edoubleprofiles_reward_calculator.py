import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict




class EdoubleprofilesRewardCalculator(BaseRewardCalculator):
    """Edoubleprofiles奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强数值提取鲁棒性"""
        import re
        candidates = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(candidates[-1]) if candidates else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """带容错的验证逻辑"""
        try:
            return int(solution) == cls._compute_answer(identity)
        except:
            return False
    
    # 其他额外方法

