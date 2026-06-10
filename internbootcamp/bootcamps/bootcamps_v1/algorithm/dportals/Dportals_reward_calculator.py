import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
import subprocess
from typing import Dict
from typing import Any
from typing import List




class DportalsRewardCalculator(BaseRewardCalculator):
    """Dportals奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> str:
        matches = re.findall(r'\[answer\]\s*(-?\d+)\s*\[/answer\]', output, re.IGNORECASE)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution: str, identity: Dict[str, Any]) -> bool:
        try:
            return int(solution.strip()) == identity['correct_output']
        except ValueError:
            return False
    
    # 其他额外方法

