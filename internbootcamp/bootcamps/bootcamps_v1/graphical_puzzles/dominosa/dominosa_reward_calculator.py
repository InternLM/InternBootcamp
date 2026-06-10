import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import itertools
import random
import re




class DominosaRewardCalculator(BaseRewardCalculator):
    """Dominosa奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        从模型输出中提取最后一个答案块并解析坐标。
        
        参数:
            output: 模型完整输出文本
            
        返回:
            list: 提取的骨牌坐标列表，格式[(坐标1, 坐标2), ...]
        """
        # 匹配最后一个答案块
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        
        dominoes = []
        last_block = answer_blocks[-1].strip()
        
        # 解析坐标对
        pattern = r'\((\d+)\s*,\s*(\d+)\)\s*,\s*\((\d+)\s*,\s*(\d+)\)'
        matches = re.findall(pattern, last_block)
        for m in matches:
            try:
                coord1 = (int(m[0]), int(m[1]))
                coord2 = (int(m[2]), int(m[3]))
                dominoes.append((coord1, coord2))
            except:
                continue
        
        return dominoes if dominoes else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证答案的完整性和正确性。
        
        参数:
            solution: 提取的骨牌坐标列表
            identity: case_generator生成的谜题实例
            
        返回:
            bool: 是否满足所有谜题约束
        """
        if not solution:
            return False

        grid = identity['grid']
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        total_cells = rows * cols
        
        # 验证覆盖完整性
        covered = set()
        pairs = []
        
        for domino in solution:
            # 校验坐标数量
            if len(domino) != 2:
                return False
            (r1, c1), (r2, c2) = domino
            
            # 校验坐标有效性
            if not (0 <= r1 < rows and 0 <= c1 < cols):
                return False
            if not (0 <= r2 < rows and 0 <= c2 < cols):
                return False
            
            # 校验相邻性
            if not ((r1 == r2 and abs(c1 - c2) == 1) or 
                    (c1 == c2 and abs(r1 - r2) == 1)):
                return False
            
            # 检查重复覆盖
            if (r1, c1) in covered or (r2, c2) in covered:
                return False
            
            covered.update([(r1, c1), (r2, c2)])
            
            # 记录数字对
            a, b = grid[r1][c1], grid[r2][c2]
            pairs.append(tuple(sorted((a, b))))
        
        # 检查覆盖率
        if len(covered) != total_cells:
            return False
        
        # 检查唯一性
        return len(pairs) == len(set(pairs))
    
    # 其他额外方法

