import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import ast
import json
import sys
import random
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.cryptomath.lib.crypto_math import generate_crypto_math




class CryptomathRewardCalculator(BaseRewardCalculator):
    """Cryptomath奖励计算器"""
    
    @staticmethod
    def extract_output(response):
        """
        Extract the output from the solution.
        
        Args:
            output: Model output to be processed.
        
        Returns:
            The processed output.
        """
        # if re.search(r'\[\[No solution\]\]', response, re.IGNORECASE):
        #     return None
        content_match = re.findall(r'\[\[(.*?)\]\]', response)
        if len(content_match) == 0:
            return None
        content = content_match[-1].replace(' ', '')
        pairs = re.findall(r'([A-Z])=(\d+)', content)
        if not pairs:
            return None
        solution = {}
        for letter, num_str in pairs:
            if not num_str.isdigit():
                return None
            num = int(num_str)
            solution[letter] = num
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return cls.check_solution(identity, solution)
    
    # 其他额外方法

