import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class DseabattleRewardCalculator(BaseRewardCalculator):
    """Dseabattle奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer_block = matches[-1].strip()
        lines = answer_block.split('\n')
        if len(lines) < 2:
            return None
        try:
            count = int(lines[0].strip())
            cells = list(map(int, lines[1].strip().split()))
            if len(cells) != count:
                return None
            return f"{count}\n{' '.join(map(str, cells))}"
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        a = identity['a']
        b = identity['b']
        s_input = identity['s']
        s = s_input + '1'
        segments = []
        prev = '1'
        start = None
        length = 0
        idx = 0
        while idx < len(s):
            if prev == '1' and s[idx] == '0':
                start = idx
                length = 0
            if s[idx] == '0':
                length += 1
            if prev == '0' and s[idx] == '1':
                segments.append((start, length))
            prev = s[idx]
            idx += 1
        positions = []
        for seg_start, seg_length in segments:
            p = seg_start + b - 1
            while p < seg_start + seg_length:
                positions.append(p + 1)
                p += b
        positions.sort()
        correct_positions = positions[a-1:]
        try:
            lines = solution.strip().split('\n')
            if len(lines) < 2:
                return False
            user_count = int(lines[0].strip())
            user_cells = list(map(int, lines[1].strip().split()))
        except:
            return False
        if user_count != len(correct_positions):
            return False
        user_set = set(user_cells)
        correct_set = set(correct_positions)
        return user_set == correct_set and len(user_cells) == user_count
    
    # 其他额外方法

