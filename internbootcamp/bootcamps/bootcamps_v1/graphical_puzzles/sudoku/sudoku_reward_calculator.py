import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random
from typing import List
from typing import Optional




class SudokuRewardCalculator(BaseRewardCalculator):
    """Sudoku奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> Optional[List[List[int]]]:
        """
        从模型输出中提取最后一个数独解
        
        参数:
            output: 包含[answer]标记的完整输出文本
            
        返回:
            二维整数矩阵，解析失败时返回None
        """
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
            
        try:
            solution = []
            for line in matches[-1].strip().split('\n'):
                nums = list(map(int, line.strip().split()))
                if nums:
                    solution.append(nums)
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution: List[List[int]], identity: dict) -> bool:
        """
        验证解的正确性
        
        参数:
            solution: 用户提交的解
            identity: 谜题实例信息
            
        返回:
            布尔值表示解的正确性
        """
        def is_valid_region(grid, row_start, col_start, size, region_size) -> bool:
            """验证子区域有效性"""
            nums = set()
            for i in range(row_start, row_start+region_size):
                for j in range(col_start, col_start+region_size):
                    num = grid[i][j]
                    if num < 1 or num > size or num in nums:
                        return False
                    nums.add(num)
            return True

        puzzle = identity["puzzle"]
        size = identity["size"]
        region_size = identity["region_rows"]
        
        # 基本维度检查
        if len(solution) != size or any(len(row) != size for row in solution):
            return False
        
        # 验证初始条件
        for i in range(size):
            for j in range(size):
                if puzzle[i][j] != 0 and solution[i][j] != puzzle[i][j]:
                    return False
        
        # 验证行、列、子区域
        valid_range = set(range(1, size+1))
        for i in range(size):
            if set(solution[i]) != valid_range:  # 行验证
                return False
            if set(solution[j][i] for j in range(size)) != valid_range:  # 列验证
                return False
            
        # 子区域验证
        for i in range(0, size, region_size):
            for j in range(0, size, region_size):
                if not is_valid_region(solution, i, j, size, region_size):
                    return False
        
        return True
    
    # 其他额外方法

