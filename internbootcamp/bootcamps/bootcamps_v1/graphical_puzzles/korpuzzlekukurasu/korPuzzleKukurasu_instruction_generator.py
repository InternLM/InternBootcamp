import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class KorpuzzlekukurasuInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzlekukurasu Bootcamp指令生成器"""
    
    def __init__(self, min_size=4, max_size=7):
        """
        初始化Korpuzzlekukurasu指令生成器
        
        Args:
            min_size: 参数描述
            max_size: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_size = min_size
        self.max_size = max_size
    
    def case_generator(self):
        """生成保证有解且具备可玩性的谜题"""
        while True:
            n = random.randint(self.min_size, self.max_size)
            grid = self._generate_valid_grid(n)
            
            row_sums = [sum(j+1 for j in range(n) if grid[i][j]) for i in range(n)]
            col_sums = [sum(i+1 for i in range(n) if grid[i][j]) for j in range(n)]
            
            # 确保至少每行/列有1个填充
            if 0 not in row_sums and 0 not in col_sums:
                return {
                    "row_sums": row_sums,
                    "col_sums": col_sums,
                    "size": n,
                    "solution": grid
                }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case["size"]
        row_str = "\n".join(
            " ".join(["X"]*n) + f" {s}" 
            for s in question_case["row_sums"]
        )
        col_str = " ".join(map(str, question_case["col_sums"]))
        
        return f"""你是一个数学谜题专家，需要解决以下网格填充问题：

网格规格：{n}x{n}正方形网格
数值说明：
- 每行右侧数字表示该行黑格子的列坐标之和（列号从左到右为1~{n}）
- 底部数字序列表示各列黑格子的行坐标之和（行号从上到下为1~{n}）

当前谜题：
{row_str}
{col_str}

答案要求：
1. 用0表示白格，1表示黑格
2. 各行数字用空格连接，行间用英文逗号分隔
3. 将最终答案包含在双中括号内

示例（4x4）：
[[1 0 0 0, 0 1 1 1, 1 0 1 0, 0 1 0 1]]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_grid(self, n):
        """生成有效初始解"""
        grid = []
        for _ in range(n):
            # 动态调整填充概率
            base_prob = 0.3 + random.random()*0.4  # 30%-70%
            grid.append([
                1 if random.random() < base_prob else 0 
                for _ in range(n)
            ])
        return grid
