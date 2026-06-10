import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from itertools import permutations




class EbracketsRewardCalculator(BaseRewardCalculator):
    """Ebrackets奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强格式鲁棒性
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip().split('\n')
        return [line.strip() for line in answer if line.strip()]
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 精确匹配生成的正确答案
        expected = identity['correct_answer']
        return solution == expected
    
    # 其他额外方法

