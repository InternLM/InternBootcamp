import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class BjohnnyandgrandmasterRewardCalculator(BaseRewardCalculator):
    """Bjohnnyandgrandmaster奖励计算器"""
    
    @staticmethod
    def extract_output(text):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', text)
        try:
            return int(matches[-1].strip()) % MOD if matches else None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        expected = case['answer']
        return (solution % MOD) == (expected % MOD)
    
    # 其他额外方法

