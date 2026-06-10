import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import ast
from typing import List
from typing import Dict
from typing import Any




class FutoshikiRewardCalculator(BaseRewardCalculator):
    """Futoshiki奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> List[List[int]]:
        """从模型输出中提取最后一个答案块"""
        answer_blocks = re.findall(
            r'\[answer\](.*?)\[/answer\]', 
            output, 
            re.DOTALL
        )
        if not answer_blocks:
            return None

        try:
            # 尝试解析最后一个答案块
            raw_answer = answer_blocks[-1].strip()
            return ast.literal_eval(raw_answer)
        except (SyntaxError, ValueError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution: List[List[int]], case: dict) -> bool:
        """完整验证解的三个核心条件"""
        n = case['size']
        initial = case['initial']
        inequalities = case['inequalities']

        # 基础结构验证
        if len(solution) != n or any(len(row)!=n for row in solution):
            return False

        # 预填数字验证
        for i in range(n):
            for j in range(n):
                if initial[i][j] != 0 and solution[i][j] != initial[i][j]:
                    return False

        # 行列唯一性验证
        valid_numbers = set(range(1, n+1))
        for row in solution:
            if set(row) != valid_numbers:
                return False
        for col in zip(*solution):
            if set(col) != valid_numbers:
                return False

        # 不等式验证
        for ineq in inequalities:
            i1, j1 = ineq['cell1']
            i2, j2 = ineq['cell2']
            a, b = solution[i1][j1], solution[i2][j2]
            if not (a > b if ineq['symbol'] == '>' else a < b):
                return False

        return True
    
    # 其他额外方法

