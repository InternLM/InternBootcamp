import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import Counter
from itertools import permutations




class KorpuzzleconnectwordsRewardCalculator(BaseRewardCalculator):
    """Korpuzzleconnectwords奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[([^\]]+)\]\]', output)
        if matches:
            last_match = matches[-1].strip().upper()
            if re.fullmatch(r'([A-Z]+\s)*[A-Z]+', last_match):
                return last_match
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # Basic parsing
            if not solution:
                return False
            answer_words = solution.split()
            expected_words = identity['solution']
            
            # Check word count
            if len(answer_words) != len(expected_words):
                return False
            
            # Verify all conditions
            used_letters = []
            for ans_word, exp_word, exp_len in zip(answer_words, expected_words, identity['word_lengths']):
                # Check length
                if len(ans_word) != exp_len:
                    return False
                # Check validity
                if ans_word.upper() not in cls.default_word_pool().get(exp_len, set()):
                    return False
                # Check letter composition
                if not set(ans_word).issubset(identity['letters']):
                    return False
                # Check duplicates
                if len(set(ans_word)) != len(ans_word):
                    return False
                used_letters.extend(list(ans_word))
            
            # Check total letters match
            return Counter(used_letters) == Counter(identity['letters'])
            
        except Exception as e:
            return False
    
    # 其他额外方法

