import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import math
import re
from typing import List
from typing import Dict
from typing import Any
from collections import defaultdict




class CilyaandthetreeRewardCalculator(BaseRewardCalculator):
    """Cilyaandthetree奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> List[int]:
        matches = re.findall(r'\[answer\]\s*(.*?)\s*\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return list(map(int, matches[-1].strip().split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_output']
    
    # 其他额外方法

