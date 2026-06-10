import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CharmonyanalysisRewardCalculator(BaseRewardCalculator):
    """Charmonyanalysis奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        return lines
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        k = identity["k"]
        n = 2 ** k
        if len(solution) != n:
            return False
        for row in solution:
            if len(row) != n or any(c not in '+*' for c in row):
                return False
        vectors = []
        for row in solution:
            vectors.append([1 if c == '+' else -1 for c in row])
        for i in range(n):
            for j in range(i + 1, n):
                if sum(a * b for a, b in zip(vectors[i], vectors[j])) != 0:
                    return False
        return True
    
    # 其他额外方法

