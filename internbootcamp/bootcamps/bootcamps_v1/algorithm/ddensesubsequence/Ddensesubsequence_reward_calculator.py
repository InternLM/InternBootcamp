import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局函数 ===

def solve(m, s):
    n = len(s)
    if n == 0 or m == 0:
        return ""
    
    # Frequency list generation
    sorted_chars = sorted(s)
    freq = []
    current_char = sorted_chars[0]
    count = 1
    
    for c in sorted_chars[1:]:
        if c == current_char:
            count += 1
        else:
            freq.append((current_char, count))
            current_char = c
            count = 1
    freq.append((current_char, count))
    
    # Find minimal solution
    for idx, (char, total) in enumerate(freq):
        required = 0
        last_covered = -1
        last_candidate = -1
        valid = True
        
        for i in range(n):
            if s[i] < char:
                last_covered = i
                last_candidate = i
            elif s[i] == char:
                last_candidate = i
            
            # Check window violation
            if i - last_covered >= m:
                if last_candidate > last_covered:
                    required += 1
                    last_covered = last_candidate
                else:
                    valid = False
                    break
        
        # Final check for the last window
        if valid and (n - last_covered) > m:
            valid = False
        
        if valid:
            # Calculate required count
            min_chars = []
            for c, _ in freq[:idx+1]:
                if c < char:
                    min_chars.append(c)
            return char * required + ''.join(sorted(min_chars))
        else:
            continue
    
    # Fallback to all smallest characters
    return ''.join(sorted(s))


class DdensesubsequenceRewardCalculator(BaseRewardCalculator):
    """Ddensesubsequence奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 多模式匹配：支持<!-- answer -->格式和不同大小写
        patterns = [
            r'\[answer\](.*?)\[/answer\]',    # 标准格式
            r'<!-- answer:?(.*?)-->',          # HTML注释格式
            r'answer:\s*(\S+)'                 # 简单前缀格式
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.DOTALL | re.IGNORECASE)
            if matches:
                clean = ''.join(filter(str.isalpha, matches[-1])).lower()
                if clean:
                    return clean
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 生成标准答案
        expected = identity['expected'].lower().strip()
        # 处理空答案情况
        if not expected:
            return solution == ''
        # 允许字符顺序不同但排序后相同
        return sorted(solution.lower()) == sorted(expected)
    
    # 其他额外方法

