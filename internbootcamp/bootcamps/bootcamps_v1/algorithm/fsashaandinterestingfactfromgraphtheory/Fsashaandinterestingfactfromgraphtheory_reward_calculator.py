import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class FsashaandinterestingfactfromgraphtheoryRewardCalculator(BaseRewardCalculator):
    """Fsashaandinterestingfactfromgraphtheory奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 正确答案计算与a,b无关，源于参考代码特性
            n = identity['n']
            m = identity['m']
            correct = cls.compute_answer(n, m)
            return (int(solution) % MOD) == (correct % MOD)
        except:
            return False
    
    # 其他额外方法

