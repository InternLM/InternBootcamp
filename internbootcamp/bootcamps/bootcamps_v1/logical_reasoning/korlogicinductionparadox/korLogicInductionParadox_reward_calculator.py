import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class KorlogicinductionparadoxRewardCalculator(BaseRewardCalculator):
    """Korlogicinductionparadox奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[([A-Ca-c])]]', output)
        return matches[-1].upper() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 基础格式验证
        if solution != identity["correct_answer"]:
            return False
        
        # 语义结构验证
        if identity["type"] == "example":
            return (
                len(identity["hypotheses"]) == 2 and
                identity["contradiction"] != "" and
                identity["phenomenon"] != ""
            )
        else:
            expr = identity["expression"]
            return (
                "→" in expr and 
                "∧" in expr and 
                ("⊻" in expr or "矛盾" in expr)
            )
    
    # 其他额外方法

