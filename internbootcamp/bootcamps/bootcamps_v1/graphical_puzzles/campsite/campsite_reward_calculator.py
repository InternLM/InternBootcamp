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
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.campsite.lib.campsite_generator import generate_campsite
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.campsite.lib.campsite_validor import validate_campsite_solution




class CampsiteRewardCalculator(BaseRewardCalculator):
    """Campsite奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        Extract the output from the solution.
        
        Args:
            output: Model output to be processed.
        
        Returns:
            The processed output.
        """
        pattern = pattern = r'```json\s*([\s\S]*?)\s*```'
        matches = re.findall(pattern, output)
        # Final-answer:{'A': [(3, 1)],
        # 'B': [(1, 4)],
        # 'C': [(2, 3)],
        # 'D': [(5, 2)],
        # 'E': [(4, 5)]}
        if matches:
            # 获取 JSON 字符串
            json_str = matches[-1]
            # print('match?', json_str)
            # print('solution generated? first lines', output[:200])
            # print('solution generated? last lines', output[-200:])
            # 替换单引号为双引号，将元组表示改为列表表示
            json_str = json_str.replace("'", '"').replace("(", "[").replace(")", "]")
            try:
                # 解析 JSON 字符串为 Python 字典
                result_dict = json.loads(json_str)
                return result_dict
            except json.JSONDecodeError as e:
                return json_str
        else:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        input_grid = identity['input_grid']
        row_constraints = identity['row_constraints']
        col_constraints = identity['col_constraints']
        input_grid = json.loads(input_grid) if type(input_grid) == str else input_grid
        row_constraints = json.loads(row_constraints) if type(row_constraints) == str else row_constraints
        col_constraints = json.loads(col_constraints) if type(col_constraints) == str else col_constraints
        is_valid, msg = validate_campsite_solution(puzzle=input_grid, row_constraints=row_constraints, col_constraints=col_constraints, solution=solution)
        return is_valid
    
    # 其他额外方法

