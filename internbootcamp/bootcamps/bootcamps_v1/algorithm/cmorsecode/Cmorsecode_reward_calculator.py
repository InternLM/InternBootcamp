import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

INVALID_4 = {"0011", "0101", "1110", "1111"}


class CmorsecodeRewardCalculator(BaseRewardCalculator):
    """Cmorsecode奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 更鲁棒的数字提取逻辑
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        
        numbers = []
        for block in answer_blocks:
            numbers.extend(re.findall(r'\d+', block))
        
        try:
            return [int(num) % MOD for num in numbers]
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['expected_outputs']
        m = identity['m']
        
        if not solution or len(solution) < m:
            return False
        
        # 取最后m个元素进行比较
        actual = solution[-m:]
        return all(
            (a % MOD) == (e % MOD) 
            for a, e in zip(actual, expected)
        )
    
    # 其他额外方法

