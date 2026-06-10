import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DbookshelvesRewardCalculator(BaseRewardCalculator):
    """Dbookshelves奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip().split()[0])
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """带缓存的高效验证"""
        try:
            return solution == cls.compute_max_beauty(
                identity["n"],
                identity["k"],
                identity["a"]
            )
        except Exception as e:
            print(f"Validation error: {str(e)}")
            return False
    
    # 其他额外方法

