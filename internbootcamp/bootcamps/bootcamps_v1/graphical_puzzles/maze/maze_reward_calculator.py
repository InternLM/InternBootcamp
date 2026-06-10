import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import ast
import json
import random
import re
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.maze.lib.maze_generator import generate_maze
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.maze.lib.maze_solver import solve_maze
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.maze.lib.maze_solver import is_path_exist
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.maze.lib.maze_validator import validate_maze_solution

# === 源文件中的全局函数 ===

def unit_test(size):
     ## Unit test
    maze_bootcamp = Mazebootcamp(size=size, difficulty=1)
    identity = maze_bootcamp.case_generator()
    print(maze_bootcamp.prompt_func(identity))
    solution = solve_maze(identity['grid'], identity['start_pos'], identity['end_pos'])[0]
    fake_output = f"""\n略，
    Final-answer: ```json
    {solution}
    ```"""
    print(fake_output)
    print("Is it correct? ",maze_bootcamp.verify_score(fake_output, identity))


class MazeRewardCalculator(BaseRewardCalculator):
    """Maze奖励计算器"""
    
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
        if matches:
            python_str = matches[-1]
            try:
                result_dict = ast.literal_eval(python_str.strip())
                return result_dict
            except Exception:
                return python_str
        else:
            return None
    
    @classmethod
    def _verify_correction(cls,solution,identity)->bool:
        return validate_maze_solution(identity['grid'], tuple(identity['start_pos']), tuple(identity['end_pos']), solution)
    
    # 其他额外方法

