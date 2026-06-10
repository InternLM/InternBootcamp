import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CslavaandtanksRewardCalculator(BaseRewardCalculator):
    """Cslavaandtanks奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        if len(lines) < 2:
            return None
        try:
            m = int(lines[0])
            bombs = list(map(int, lines[1].split()))
            if len(bombs) != m:
                return None
            return [m] + bombs
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or len(solution) < 1:
            return False
        m, bombs = solution[0], solution[1:]
        n = identity['n']
        
        # 前置校验：次数符合理论最小值
        if m != n + (n // 2):
            return False
        
        # 快速校验：炸弹顺序必须覆盖所有关键模式
        expected_bomb_pattern = (
            [i for i in range(2, n+1, 2)] + 
            [i for i in range(1, n+1, 2)] + 
            [i for i in range(2, n+1, 2)]
        )
        if bombs != expected_bomb_pattern:
            return False

        return True
    
    # 其他额外方法

