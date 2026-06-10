import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import json
import random
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.starbattle.lib.get_grid import generate_star_battle_grid
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.starbattle.lib.dfs_solver_cn import print_grid_in_kor




class StarbattleInstructionGenerator(BaseInstructionGenerator):
    """Starbattle Bootcamp指令生成器"""
    
    def __init__(self, size=5):
        """
        初始化Starbattle指令生成器
        
        Args:
            size: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.size = size
    
    def case_generator(self):
        grid = self.generator()

        return {
            "input_grid": grid
        }
    
    def prompt_func(self, identity) -> str:
        """
        Process the input_data and return the processed prompt.
        
        Args:
            question_ori: The question to be processed.
        
        Returns:
            str: The processed prompt.
        """

        statements = [f"""### 核心职责:

1. 规则分析:
   - 解码并理解所提供的谜题规则 
   - 创建一个系统化的规则实施方法
   - 识别潜在的规则相互作用或依赖关系

2. 解决方案开发:
   - 有条理地将规则应用于谜题场景
   - 开发分步解决策略
   - 在整个解题过程中保持准确性

3. 质量保证:
   - 反复检查解决方案的有效性
   - 确保遵守所有规定规则
   - 根据初始条件验证最终结果

### 谜题参数:
1. 网格结构: 游戏区域由不同的区域(分区)组成,每个区域包含多个方格。

2. 星星放置指南:
   - 星星必须均匀分布,每行每列1个星星
   - 每个分区需要恰好1个星星
   - 星星必须保持分离(不能相邻,包括对角线)

3. 输入格式:
   - 采用字母指定区域的矩阵表示
   - 每个独特字母代表一个不同的分区 
   - 示例: A区域包括所有标记为'A'的方格

4. 解决方案格式:
   - 基于坐标的报告系统
   - 格式: [区域字母]:(行坐标,列坐标)
   - 每个区域根据需要列出多个坐标
   
   ###Question

   初始网格为:\n {print_grid_in_kor(identity['input_grid'])}

   """,
   f"""star battle是一种逻辑解谜游戏，其规则简单，解题过程富有挑战性。
游戏规则 很简单。
按如下要求在格子上放置星星：
- 任意两颗星星不能在横向、纵向或对角上相邻。
- 每行、每列及每个区域上需放置1颗星星。
网格由矩阵表示，每个字母表示该位置所在区域的ID
请完成该star battle，初始网格为:\n {print_grid_in_kor(identity['input_grid'])}"""]
        
        instruction_following = """Please note that the coordinate system used in this task starts from (1, 1). This means:
1. The first row and first column are both numbered 1, not 0.
2. In any coordinate (x, y), x represents the row number, and y represents the column number, with both x and y having a minimum value of 1.
3. When processing coordinate data, ensure all calculations and logic are based on (1, 1) as the starting point to avoid errors caused by misunderstandings of the coordinate system.

Let's think step by step and output the final answer with an example json formatting for a 5x5 board: 
Final-answer: ```json
{'A': [(row_a, col_a)],'B': [(row_b, col_b)],'C': [(row_c, col_c)],'D': [(row_d, col_d)],'E': [(row_e, col_e)]}
```"""
        prompt = statements[random.randint(0,len(statements)-1)] + '\n' + instruction_following
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generator(self):
        self.grid, self.star_positions = generate_star_battle_grid(self.size)
        return self.grid
