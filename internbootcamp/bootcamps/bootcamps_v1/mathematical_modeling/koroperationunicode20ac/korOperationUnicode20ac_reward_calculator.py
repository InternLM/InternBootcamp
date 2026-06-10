import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import math
import ast




class Koroperationunicode20acRewardCalculator(BaseRewardCalculator):
    """Koroperationunicode20ac奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        def safe_parse(s):
            try:
                parsed = ast.literal_eval(s)
                if not isinstance(parsed, tuple) or not all(isinstance(row, tuple) for row in parsed):
                    return None
                return parsed
            except:
                return None

        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
            
        clean_str = re.sub(r'\s+', '', matches[-1].strip())
        return safe_parse(clean_str)  # 移除破坏性字符处理
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        A = identity['A']
        B = identity['B']
        
        try:
            # 维度校验
            if (len(solution) != len(A)) or any(len(s_row) != len(a_row) for s_row, a_row in zip(solution, A)):
                return False
            
            # 元素校验
            for i_row, (a_row, b_row) in enumerate(zip(A, B)):
                for j_col, (a, b) in enumerate(zip(a_row, b_row)):
                    expected = 2 * a + 3 * b
                    actual = solution[i_row][j_col]
                    if not math.isclose(expected, actual, rel_tol=1e-9, abs_tol=1e-9):
                        return False
            return True
        except (TypeError, IndexError):
            return False
    
    # 其他额外方法

