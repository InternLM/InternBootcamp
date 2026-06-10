import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import json
import random
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.arrowmaze.lib.maze_generator import generate_arrow_maze




class ArrowmazeInstructionGenerator(BaseInstructionGenerator):
    """Arrowmaze Bootcamp指令生成器"""
    
    def __init__(self, size:tuple = (6,6), start_pos:tuple = (0,0), end_pos:tuple = (5,5), max_solution_step:int = 5, seed:int = None):
        """
        初始化Arrowmaze指令生成器
        
        Args:
            size: 参数描述
            start_pos: 参数描述
            end_pos: 参数描述
            max_solution_step: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.size = size
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.max_solution_step = max_solution_step
        self.seed = seed
    
    def case_generator(self):
        if self.max_solution_step < 2:
            raise ValueError
        grid = generate_arrow_maze(self.size[0], self.size[1], tuple(self.start_pos), tuple(self.end_pos), max_attempts= 20 ,max_solution_step=self.max_solution_step, seed=self.seed)
        return {
            "input_grid": grid,
            "start_position": self.start_pos
        }
    
    def prompt_func(self, identity) -> str:
        """
        Process the input_data and return the processed prompt.
        
        Args:
            question_ori: The question to be processed.
        
        Returns:
            str: The processed prompt.
        """

        statements = [f"""You are an intelligent assistant specializing in solving custom puzzle problems. Below is a specific rule defined for a custom puzzle. Your task is to apply this rule accurately to the provided question.

    ### Instructions:

    1. Thoroughly understand the rule provided. If needed, break down the rule into simpler components or steps.
    2. Apply the rule carefully to address the question presented.
    3. Verify your answer to ensure it aligns with the rule and the context of the puzzle.
### Puzzle Rule:
1.The maze consists of a grid with an arrow in each grid cell pointing in one of eight directions up, down, left, right, or diagonally.
2.The maze has a well-defined start and end point.
3.The player starts at the starting point, moves to the next grid cell in the direction indicated by the arrow, and then continues to move as indicated by the arrow in the new grid.
4.The player must move strictly in the direction indicated by the arrows and cannot go in the opposite direction or choose another path.
5.The game is won when the player successfully reaches the end from the starting point.

### Question

Now the grid of the arrow maze is:\n{identity["input_grid"]}
The start position is {identity["start_position"]} and the end position is 'o' in the grid.

The answers are required to point out the position of each inflection point in order, 0 indicates a point not on the path.
""",
f"""
The arrow maze is a puzzle game. The rule of arrow maze is:
1.The maze consists of a grid with an arrow in each grid cell pointing in one of eight directions up, down, left, right, or diagonally.
2.The maze has a well-defined start and end point.
3.The player starts at the starting point, moves to the next grid cell in the direction indicated by the arrow, and then continues to move as indicated by the arrow in the new grid.
4.The player must move strictly in the direction indicated by the arrows and cannot go in the opposite direction or choose another path.
5.The game is won when the player successfully reaches the end from the starting point.

Now the grid of the arrow maze is:\n{identity["input_grid"]}
The start position is {identity["start_position"]} and the end position is 'o' in the grid.
"""
,
f"""你是一个擅长解决自定义谜题问题的智能助手。以下是为一个自定义谜题所定义的特定规则。你的任务是将该规则准确应用到所提供的问题上。
说明：
透彻理解所提供的规则。如有需要，将规则拆解为更简单的组成部分或步骤。
仔细运用规则来解决给出的问题。
核实你的答案，确保其与规则以及谜题的情境相符。
谜题规则：
迷宫由一个网格构成，每个网格单元格中有一个箭头，指向八个方向之一，即上、下、左、右或对角线方向。
迷宫有明确规定的起点和终点。
玩家从起点出发，按照箭头所指方向移动到下一个网格单元格，然后继续按照新网格中箭头所指方向移动。
玩家必须严格按照箭头指示的方向移动，不能朝相反方向移动或选择其他路径。
当玩家成功从起点抵达终点时，游戏获胜。
问题
现在箭头迷宫的网格如下：
\n{identity["input_grid"]}

起点位置是 (0, 0)，终点位置是网格中的 “○”。
答案需要按顺序指出每个转折点的位置，0 表示不在路径上的点。
"""

]

        instr = statements[random.randint(0,len(statements)-1)]
        instruction_following = """Let's think step by step and output the final answer with an example json formatting: 
Final-answer: ```json
[[A, B, C, D],
[E, F, G, H],
[I, J, K, L],
[M, N, O, P]]
```"""
        prompt = instr + '\n' + instruction_following
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

