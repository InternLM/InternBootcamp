import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import re
from typing import Dict
from typing import List
from typing import Tuple




class PipesRewardCalculator(BaseRewardCalculator):
    """Pipes奖励计算器"""
    
    @staticmethod
    def extract_output(output: str):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            solution = json.loads(matches[-1].strip())
            converted = {}
            for color, path in solution.items():
                converted_path = []
                for coord in path:
                    if isinstance(coord, list) and len(coord) == 2:
                        converted_path.append(tuple(coord))
                    else:
                        return None
                converted[color] = converted_path
            return converted
        except json.JSONDecodeError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution: Dict[str, List[Tuple[int, int]]], identity: dict) -> bool:
        endpoints = {color: [tuple(ep) for ep in eps] for color, eps in identity['endpoints'].items()}
        grid_size = tuple(identity['grid_size'])
        all_coords = set()

        if set(solution.keys()) != set(endpoints.keys()):
            return False

        for color, path in solution.items():
            if len(path) < 2:
                return False
            start, end = path[0], path[-1]
            expected = set(endpoints[color])
            if {start, end} != set(expected):
                return False

            prev = path[0]
            for coord in path[1:]:
                dx, dy = abs(coord[0]-prev[0]), abs(coord[1]-prev[1])
                if dx + dy != 1:
                    return False
                prev = coord

            for coord in path:
                if coord in all_coords:
                    return False
                all_coords.add(coord)

        expected_coords = {(i, j) for i in range(grid_size[0]) for j in range(grid_size[1])}
        if all_coords != expected_coords:
            return False

        for color, path in solution.items():
            other_eps = set()
            for other_color in endpoints:
                if other_color != color:
                    other_eps.update(tuple(ep) for ep in endpoints[other_color])
            for coord in path[1:-1]:
                if coord in other_eps:
                    return False

        return True
    
    # 其他额外方法

