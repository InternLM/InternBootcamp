import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class KorpuzzlewordsearchRewardCalculator(BaseRewardCalculator):
    """Korpuzzlewordsearch奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        solution = []
        for line in content.split('\n'):
            line = line.strip()
            match = re.match(r'^(\w+)\s*\((\d+),(\d+)\)\((\d+),(\d+)\)$', line)
            if match:
                solution.append((
                    match.group(1).upper(),
                    (int(match.group(2)), int(match.group(3))),
                    (int(match.group(4)), int(match.group(5)))
                ))
        return solution if solution else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        grid = identity["grid"]
        word_list = [w.upper() for w in identity["word_list"]]
        
        if len(solution) != len(word_list):
            return False
        
        for i, (word, start, end) in enumerate(solution):
            target_word = word_list[i]
            if word.upper() != target_word:
                return False

            sr, sc = start
            er, ec = end
            length = len(target_word)

            dy = er - sr
            dx = ec - sc

            try:
                step_y = dy // (length-1) if length > 1 else dy
                step_x = dx // (length-1) if length > 1 else dx
            except ZeroDivisionError:
                return False

            if length > 1 and (abs(step_x) not in (0,1) or abs(step_y) not in (0,1)):
                return False

            formed = []
            for j in range(length):
                r = sr + j*step_y
                c = sc + j*step_x
                if not (0 <= r < len(grid) and 0 <= c < len(grid[0])):
                    return False
                formed.append(grid[r][c].upper())

            formed_str = ''.join(formed)
            if formed_str not in (target_word, target_word[::-1]):
                return False
        
        return True
    
    # 其他额外方法

