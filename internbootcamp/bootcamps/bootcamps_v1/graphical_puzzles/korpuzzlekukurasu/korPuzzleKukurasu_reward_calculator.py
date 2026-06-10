import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class KorpuzzlekukurasuRewardCalculator(BaseRewardCalculator):
    """Korpuzzlekukurasu奖励计算器"""
    
    @staticmethod 
    def extract_output(output):
        # 兼容中文括号和超长上下文
        pattern = r'\[{2}[^\[\]]*\]{2}'
        matches = re.findall(pattern, output)
        if not matches:
            return None
            
        last_match = matches[-1].strip('[]')
        # 统一处理中文标点
        processed = re.sub(r'[，]', ',', last_match)
        processed = re.sub(r'\s+', ' ', processed).strip()
        
        # 二次清洗
        rows = []
        for r in processed.split(','):
            clean_row = re.sub(r'[^\d\s]', '', r).strip()
            if clean_row:
                rows.append(clean_row)
                
        return ', '.join(rows) if rows else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity["size"]
            # 格式验证
            if not re.fullmatch(r'([01] )+[01](, ([01] )+[01])*', solution):
                return False
                
            grid = []
            for row in solution.split(', '):
                elements = list(map(int, row.split()))
                if len(elements) != n:
                    return False
                grid.append(elements)
            
            # 数学验证
            row_valid = all(
                sum(j+1 for j in range(n) if grid[i][j]) == identity["row_sums"][i]
                for i in range(n)
            )
            col_valid = all(
                sum(i+1 for i in range(n) if grid[i][j]) == identity["col_sums"][j]
                for j in range(n)
            )
            
            return row_valid and col_valid
        except:
            return False
    
    # 其他额外方法

