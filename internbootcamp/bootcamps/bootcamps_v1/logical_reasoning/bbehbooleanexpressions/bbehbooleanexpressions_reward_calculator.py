import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
import math
from itertools import count




class BbehbooleanexpressionsRewardCalculator(BaseRewardCalculator):
    """Bbehbooleanexpressions奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        Extract the answer from the model's response.
        
        Args:
            output: The model's complete response
            
        Returns:
            str: The extracted answer (A, B, C, D, or E) or None if not found
        """
        # Look for the answer in the [answer] tags
        pattern = r'\[answer\](.*?)\[\/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        
        if not matches:
            return None
        
        # Get the last match (in case there are multiple)
        last_match = matches[-1].strip()
        
        # Normalize to just the letter
        if last_match and len(last_match) >= 1:
            answer = last_match[0].upper()
            
            # Validate the answer is one of the valid options
            if answer in ['A', 'B', 'C', 'D', 'E']:
                return answer
        
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity) -> bool:
        """
        Verify if the provided solution is correct.
        
        Args:
            solution: The extracted solution (A, B, C, D, or E)
            identity: The puzzle case dictionary
            
        Returns:
            bool: True if the solution is correct, False otherwise
        """
        # Convert the solution letter to the index
        if solution is None:
            return False
        
        solution_index = ord(solution) - ord('A')
        
        # Check if the solution matches the correct answer
        return solution_index == identity["answer"]
    
    # 其他额外方法

