import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class DnashmatrixRewardCalculator(BaseRewardCalculator):
    """Dnashmatrix奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """从模型输出中提取最后一个答案块"""
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """验证答案正确性，根据identity中的有效性标记"""
        solution_lines = solution.strip().splitlines()
        if not solution_lines:
            return False
        first_line = solution_lines[0].strip().upper()
        is_valid_case = identity.get("is_valid", True)

        if is_valid_case:
            # 案例有效，模型应返回VALID并给出正确网格
            if first_line != "VALID":
                return False
            return cls.check_valid_solution(solution_lines, identity)
        else:
            # 案例无效，模型应返回INVALID
            return first_line == "INVALID"
    
    # 其他额外方法

