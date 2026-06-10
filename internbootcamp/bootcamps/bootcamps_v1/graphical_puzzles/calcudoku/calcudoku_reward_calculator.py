import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import ast
import json
import sys
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.calcudoku.lib.calcudoku_generator import CalcudokuGenerator
import random




class CalcudokuRewardCalculator(BaseRewardCalculator):
    """Calcudoku奖励计算器"""
    
    @staticmethod
    def extract_output(response):
        """
        Extract the output from the solution.
        
        Args:
            output: Model output to be processed.
        
        Returns:
            The processed output.
        """
        # 提取双括号中的内容
        match = re.findall(r'\[\[(.*?)\]\]', response, re.DOTALL)
        if len(match) == 0:
            return None
        content = match[-1]
        rows = [row.strip('[] ') for row in content.split(',')]
        solution = []
        for row in rows:
            try:
                numbers = list(map(int, row.strip().split()))
            except:
                return None
            solution.append(numbers)
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return cls.check_solution(identity, solution)
    
    # 其他额外方法

