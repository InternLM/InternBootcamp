import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CvaleraandtubesRewardCalculator(BaseRewardCalculator):
    """Cvaleraandtubes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        lines = output.split('\n')
        answer_blocks = []
        current_block = []
        in_answer = False

        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('[answer]'):
                in_answer = True
                current_block = []
            elif stripped_line.startswith('[/answer]'):
                in_answer = False
                if current_block:
                    answer_blocks.append(current_block)
                    current_block = []
            elif in_answer:
                current_block.append(stripped_line)

        if not answer_blocks:
            return None

        last_block = answer_blocks[-1]
        tubes = []

        for line in last_block:
            parts = line.split()
            if not parts:
                continue
            if len(parts) < 3:
                continue

            try:
                r_i = int(parts[0])
            except ValueError:
                continue

            if len(parts) != 1 + 2 * r_i:
                continue

            if r_i < 2:
                continue

            try:
                coords = []
                for i in range(r_i):
                    x = int(parts[1 + 2 * i])
                    y = int(parts[2 + 2 * i])
                    coords.append((x, y))
                tubes.append(coords)
            except (ValueError, IndexError):
                continue

        return tubes or None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False

        n = identity['n']
        m = identity['m']
        k = identity['k']

        if len(solution) != k:
            return False

        for tube in solution:
            if len(tube) < 2:
                return False

        all_cells = set()
        for tube in solution:
            for (x, y) in tube:
                if x < 1 or x > n or y < 1 or y > m:
                    return False
                if (x, y) in all_cells:
                    return False
                all_cells.add((x, y))

        if len(all_cells) != n * m:
            return False

        for tube in solution:
            prev = tube[0]
            visited = {prev}
            for current in tube[1:]:
                dx = abs(current[0] - prev[0])
                dy = abs(current[1] - prev[1])
                if dx + dy != 1:
                    return False
                if current in visited:
                    return False
                visited.add(current)
                prev = current

        return True
    
    # 其他额外方法

