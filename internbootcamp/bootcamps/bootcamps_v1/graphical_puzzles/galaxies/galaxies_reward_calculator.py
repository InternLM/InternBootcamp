import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
from ast import literal_eval
from collections import deque




class GalaxiesRewardCalculator(BaseRewardCalculator):
    """Galaxies奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """Extracts last valid answer block from LLM output"""
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return literal_eval(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """Validates solution against puzzle constraints"""
        try:
            # Validate solution structure
            if not cls._validate_structure(solution):
                return False

            # Check center consistency
            if not cls._check_centers(solution, identity['centers']):
                return False

            # Check grid coverage
            if not cls._check_coverage(solution, identity['rows'], identity['cols']):
                return False

            # Validate each galaxy
            for galaxy in solution:
                if not cls._validate_galaxy(galaxy):
                    return False
            return True
        except:
            return False
    
    # 其他额外方法

