import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class ThermometersRewardCalculator(BaseRewardCalculator):
    """Thermometers奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        rows = [line.strip() for line in last_answer.split('\n') if line.strip()]
        try:
            grid = [list(map(int, row.split())) for row in rows]
            if all(len(row) == len(grid[0]) for row in grid) and len(grid) == len(grid[0]):
                return grid
        except ValueError:
            pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        size = identity['size']
        enforce_latin = identity.get('enforce_latin', True)
        thermometers = identity['thermometers']

        if len(solution) != size or any(len(row) != size for row in solution):
            return False
        if any(not (1 <= num <= size) for row in solution for num in row):
            return False

        if enforce_latin:
            expected = list(range(1, size+1))
            for row in solution:
                if sorted(row) != expected:
                    return False
            for col in range(size):
                if sorted(row[col] for row in solution) != expected:
                    return False

        for thermo in thermometers:
            path = thermo['path']
            values = [solution[r][c] for (r, c) in path]
            if any(values[i] >= values[i+1] for i in range(len(values)-1)):
                return False

        return True
    
    # 其他额外方法

