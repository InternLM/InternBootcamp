import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class FgameRewardCalculator(BaseRewardCalculator):
    """Fgame奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        从模型输出中提取答案。
        """
        answer_pattern = re.compile(r'\[answer\](.*?)\[/answer\]', re.DOTALL)
        matches = answer_pattern.findall(output)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        solutions = []
        for line in last_answer.split('\n'):
            line = line.strip()
            if line:
                try:
                    solutions.append(float(line))
                except ValueError:
                    continue
        return solutions if solutions else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证答案是否正确。
        """
        if not solution or len(solution) != identity['r'] + 1:
            return False

        n = identity['n']
        initial = identity['initial'].copy()
        updates = identity['updates']
        total = sum(initial)
        expected = [total / (2 ** n)]
        current_values = initial.copy()

        for update in updates:
            z = update['z']
            g = update['g']
            total += g - current_values[z]
            current_values[z] = g
            expected.append(total / (2 ** n))

        if len(solution) != len(expected):
            return False

        for s, e in zip(solution, expected):
            if abs(s - e) > 1e-6 and abs(s - e) / max(1, abs(e)) > 1e-6:
                return False
        return True
    
    # 其他额外方法

