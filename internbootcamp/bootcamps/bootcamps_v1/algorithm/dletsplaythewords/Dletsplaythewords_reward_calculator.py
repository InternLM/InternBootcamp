import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局函数 ===

def solve_case(words):
    count = [0] * 4  # 00, 01, 10, 11
    swap = [[] for _ in range(4)]
    items = set(words)
    
    for i, s in enumerate(words):
        a = s[0]
        b = s[-1]
        pos = int(a) * 2 + int(b)
        count[pos] += 1
        reversed_s = s[::-1]
        if reversed_s not in items:
            swap[pos].append(i + 1)  # Using 1-based index
    
    if count[1] > count[2]:
        count[1], count[2] = count[2], count[1]
        swap[1], swap[2] = swap[2], swap[1]
    
    if count[1] + count[2] == 0:
        if count[0] > 0 and count[3] > 0:
            return (-1, None)
        else:
            return (0, [])
    else:
        diff = 0
        original_count_01 = count[1]
        original_count_10 = count[2]
        while count[2] - count[1] > 1:
            diff += 1
            count[2] -= 1
            count[1] += 1
        i = 1 if len(swap[1]) > len(swap[2]) else 2
        if len(swap[i]) >= diff:
            indexes = swap[i][:diff]
            return (diff, indexes)
        else:
            return (-1, None)


class DletsplaythewordsRewardCalculator(BaseRewardCalculator):
    """Dletsplaythewords奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        if not lines:
            return None
        first_line = lines[0]
        if first_line == '-1':
            return -1
        try:
            k = int(first_line)
        except:
            return None
        if k < 0:
            return None
        if k == 0:
            return []
        if len(lines) < 2:
            return None
        indexes = []
        if not lines[1]:
            return None
        for s in lines[1].split():
            try:
                idx = int(s)
                indexes.append(idx)
            except:
                return None
        return indexes
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        words = identity['words']
        n = identity['n']
        if solution == -1:
            correct_k = identity['correct_k']
            if correct_k != -1:
                return False
            return True  # Assume case_generator's solve_case is correct
        if not isinstance(solution, list):
            return False
        k = len(solution)
        valid_indices = set(range(1, n+1))
        seen_indices = set()
        for idx in solution:
            if idx not in valid_indices or idx in seen_indices:
                return False
            seen_indices.add(idx)
        modified_words = []
        seen_words = set()
        for i, word in enumerate(words):
            idx = i + 1
            if idx in solution:
                modified = word[::-1]
            else:
                modified = word
            if modified in seen_words:
                return False
            seen_words.add(modified)
            modified_words.append(modified)
        count = defaultdict(int)
        for word in modified_words:
            start = word[0]
            end = word[-1]
            type_ = f"{start}{end}"
            if type_ == "00":
                count['00'] += 1
            elif type_ == "01":
                count['01'] += 1
            elif type_ == "10":
                count['10'] += 1
            elif type_ == "11":
                count['11'] += 1
        c01 = count['01']
        c10 = count['10']
        if abs(c01 - c10) > 1:
            return False
        if (c01 + c10) == 0:
            if count['00'] > 0 and count['11'] > 0:
                return False
        return True
    
    # 其他额外方法

