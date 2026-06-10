import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import json
import random
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.starbattle.lib.get_grid import generate_star_battle_grid
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.starbattle.lib.dfs_solver_cn import print_grid_in_kor




class StarbattleRewardCalculator(BaseRewardCalculator):
    """Starbattle奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        Extract the output from the solution.
        
        Args:
            output: Model output to be processed.
        
        Returns:
            The processed output.
        """
        pattern = pattern = r'```json\s*(\{[\s\S]*?\})\s*```'
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
    def _verify_correction(cls, solution, identuty:dict)->bool:
        """
        Verify the correction of the solution.
        """ 
        input_grid = json.loads(identuty['input_grid']) if type(identuty['input_grid']) == str else identuty['input_grid']
        n = identuty.pop('n', 1)
        # Check each star is in the correct region
        for region, coords in solution.items():
            for (row, col) in coords:
                if row < 1 or row > len(input_grid) or col < 1 or col > len(input_grid[0]):
                    return False
                if input_grid[row-1][col-1] != region:
                    return False
        
        # Check each region has exactly n stars
        for region, coords in solution.items():
            if len(coords) != n:
                return False
        
        # Collect all stars and check row/column counts
        all_stars = [coord for coords in solution.values() for coord in coords]
        rows = {}
        cols = {}
        for (r, c) in all_stars:
            rows[r] = rows.get(r, 0) + 1
            cols[c] = cols.get(c, 0) + 1
        if any(v != n for v in rows.values()) or any(v != n for v in cols.values()):
            return False
        
        # Check adjacency
        for i in range(len(all_stars)):
            for j in range(i+1, len(all_stars)):
                r1, c1 = all_stars[i]
                r2, c2 = all_stars[j]
                if abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1:
                    return False
        
        return True
    
    # 其他额外方法

