import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_min_removals(n, m, table_rows):
    sol = ['' for _ in range(n)]
    count = 0
    for col_idx in range(m):
        current_col = [row[col_idx] for row in table_rows]
        temp = [sol[i] + current_col[i] for i in range(n)]
        if temp == sorted(temp):
            sol = temp
        else:
            count += 1
    return count


class AremovingcolumnsRewardCalculator(BaseRewardCalculator):
    """Aremovingcolumns奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        try:
            return int(answer_blocks[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct']  # 确保与case_generator的键一致
    
    # 其他额外方法

