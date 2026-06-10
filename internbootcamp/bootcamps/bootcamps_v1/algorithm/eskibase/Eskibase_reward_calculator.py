import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

mod = 10**9 + 9


class EskibaseRewardCalculator(BaseRewardCalculator):
    """Eskibase奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        
        # 提取最后一个有效答案块并验证完整性
        last_block = answer_blocks[-1].strip()
        solutions = []
        valid_lines = 0
        
        for line in last_block.split('\n'):
            line = line.strip()
            if line:
                try:
                    num = int(line) % mod
                    solutions.append(num)
                    valid_lines += 1
                except ValueError:
                    continue
        
        # 严格验证行数匹配
        if valid_lines != len(solutions) or valid_lines == 0:
            return None
        return solutions
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 严格验证答案长度和内容
        return solution == identity['expected_outputs'] if solution else False
    
    # 其他额外方法

