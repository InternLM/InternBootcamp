import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CswaplettersRewardCalculator(BaseRewardCalculator):
    """Cswapletters奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        content = answer_blocks[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            return None
        first_line = lines[0]
        if first_line == '-1':
            return -1
        try:
            k = int(first_line)
        except ValueError:
            return None
        if k < 0:
            return None
        remaining_lines = lines[1:]
        if len(remaining_lines) != k:
            return None
        operations = []
        for line in remaining_lines:
            parts = line.split()
            if len(parts) != 2:
                return None
            try:
                pos1 = int(parts[0])
                pos2 = int(parts[1])
                operations.append((pos1, pos2))
            except ValueError:
                return None
        return (k, operations)
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        s = identity['s']
        t = identity['t']
        n = identity['n']

        def calculate_min_operations(s, t, n):
            count_a_s = s.count('a')
            count_a_t = t.count('a')
            total_a = count_a_s + count_a_t
            if total_a % 2 != 0:
                return -1, None
            ab = []
            ba = []
            for i in range(n):
                sc = s[i]
                tc = t[i]
                if sc != tc:
                    if sc == 'a':
                        ab.append(i + 1)
                    else:
                        ba.append(i + 1)
            if (len(ab) % 2) != (len(ba) % 2):
                return -1, None
            operations = []
            ans = (len(ab) // 2) + (len(ba) // 2)
            for i in range(0, len(ab) - 1, 2):
                operations.append((ab[i], ab[i + 1]))
            for i in range(0, len(ba) - 1, 2):
                operations.append((ba[i], ba[i + 1]))
            if len(ab) % 2 == 1 and len(ba) % 2 == 1:
                ans += 2
                a_last = ab[-1]
                b_last = ba[-1]
                operations.append((a_last, a_last))
                operations.append((a_last, b_last))
            return ans, operations

        correct_ans, correct_ops = calculate_min_operations(s, t, n)
        if correct_ans == -1:
            return solution == -1
        if solution == -1:
            return False
        user_k, user_ops = solution
        if user_k != correct_ans:
            return False
        if len(user_ops) != user_k:
            return False
        for op in user_ops:
            pos1, pos2 = op
            if not (1 <= pos1 <= n and 1 <= pos2 <= n):
                return False
        s_list = list(s)
        t_list = list(t)
        for pos1_s, pos2_t in user_ops:
            pos1 = pos1_s - 1
            pos2 = pos2_t - 1
            s_list[pos1], t_list[pos2] = t_list[pos2], s_list[pos1]
        return s_list == t_list
    
    # 其他额外方法

