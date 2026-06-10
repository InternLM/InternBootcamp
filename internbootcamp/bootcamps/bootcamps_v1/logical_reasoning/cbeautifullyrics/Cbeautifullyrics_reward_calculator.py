import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import random
from collections import defaultdict

# === 源文件中的全局函数 ===

def count_vowels_and_last_vowel(word):
    vowels = {'a', 'e', 'i', 'o', 'u'}
    count = 0
    last_v = None
    for c in word:
        if c in vowels:
            count += 1
            last_v = c
    return count, last_v

def extract_all_vowels(word):
    vowels = {'a', 'e', 'i', 'o', 'u'}
    return [c for c in word if c in vowels]


class CbeautifullyricsRewardCalculator(BaseRewardCalculator):
    """Cbeautifullyrics奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        return last_match
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        
        lines = [line.strip() for line in solution.split('\n') if line.strip()]
        if not lines:
            return False
        
        try:
            m = int(lines[0])
        except:
            return False
        
        if m != identity['expected_m']:
            return False
        
        if len(lines) != 1 + 2 * m:
            return False
        
        lyrics = []
        for i in range(m):
            line1 = lines[1 + 2*i].split()
            line2 = lines[2 + 2*i].split()
            if len(line1) != 2 or len(line2) != 2:
                return False
            lyrics.append((line1, line2))
        
        # Check each lyric's conditions
        for (first_line, second_line) in lyrics:
            a1, a2 = first_line
            b1, b2 = second_line

            # Condition 1
            a1_v, _ = count_vowels_and_last_vowel(a1)
            b1_v, _ = count_vowels_and_last_vowel(b1)
            if a1_v != b1_v:
                return False

            # Condition 2
            a2_v, _ = count_vowels_and_last_vowel(a2)
            b2_v, _ = count_vowels_and_last_vowel(b2)
            if a2_v != b2_v:
                return False

            # Condition 3
            line1_vowels = extract_all_vowels(a1) + extract_all_vowels(a2)
            line2_vowels = extract_all_vowels(b1) + extract_all_vowels(b2)
            if not line1_vowels or not line2_vowels:
                return False
            if line1_vowels[-1] != line2_vowels[-1]:
                return False

        # Check word usage counts
        word_counts = defaultdict(int)
        for word in identity['words']:
            word_counts[word] += 1
        used = defaultdict(int)
        for (line1, line2) in lyrics:
            for word in line1 + line2:
                used[word] += 1
                if used[word] > word_counts.get(word, 0):
                    return False

        return True
    
    # 其他额外方法

