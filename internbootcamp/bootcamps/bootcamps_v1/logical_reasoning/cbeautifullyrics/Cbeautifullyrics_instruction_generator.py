import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class CbeautifullyricsInstructionGenerator(BaseInstructionGenerator):
    """Cbeautifullyrics Bootcamp指令生成器"""
    
    def __init__(self, max_words=10, min_words=4, mode='solvable'):
        """
        初始化Cbeautifullyrics指令生成器
        
        Args:
            max_words: 参数描述
            min_words: 参数描述
            mode: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_words = max_words
        self.min_words = min_words
        self.mode = mode  # 'solvable' or 'unsolvable'
    
    def case_generator(self):
        if self.mode == 'solvable':
            words, expected_m = self._generate_solvable_case()
        else:
            words, expected_m = self._generate_unsolvable_case()
        return {
            'n': len(words),
            'words': words,
            'expected_m': expected_m,
            'word_counts': defaultdict(int, {word: words.count(word) for word in words})
        }
    
    @staticmethod
    def prompt_func(question_case):
        words = question_case['words']
        example_input = "\n".join(words)
        prompt = f"""You are given {question_case['n']} words, each consisting of lowercase letters. Each word contains at least one vowel. Your task is to form as many beautiful lyrics as possible.

A beautiful lyric consists of two lines. Each line has two words separated by a space. The conditions are:
1. The number of vowels in the first word of each line must be equal.
2. The number of vowels in the second word of each line must be equal.
3. The last vowel in the entire first line must be the same as the last vowel in the entire second line.

Vowels are 'a', 'e', 'i', 'o', 'u' (excluding 'y').

Input:
{question_case['n']}
{example_input}

Output format:
- The first line is the maximum number of lyrics, m.
- Followed by 2m lines, each pair forming a lyric.

Put your answer within [answer] tags. Example:
[answer]2[/answer]
word1 word2
word3 word4
word5 word6
word7 word8"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_solvable_case(self):
        # Generate at least one valid lyric
        words = []
        # Generate one valid lyric with 4 unique words
        a = self._generate_word_with_vowel_count(2)
        c = self._generate_word_with_vowel_count(2)
        b = self._generate_word_with_vowel_count_and_last(1, 'a')
        d = self._generate_word_with_vowel_count_and_last(1, 'a')
        words.extend([a, b, c, d])
        # Ensure expected_m is 1 for this simple case
        expected_m = 1
        return words, expected_m

    def _generate_unsolvable_case(self):
        # Generate words that cannot form any lyric
        words = [
            self._generate_word_with_vowel_count_and_last(1, 'a'),
            self._generate_word_with_vowel_count_and_last(2, 'e'),
            self._generate_word_with_vowel_count_and_last(3, 'i'),
            self._generate_word_with_vowel_count_and_last(4, 'o')
        ]
        return words, 0

    def _generate_word_with_vowel_count(self, count):
        vowels = ['a', 'e', 'i', 'o', 'u']
        other = [chr(c) for c in range(ord('a'), ord('z')+1) if chr(c) not in vowels]
        parts = []
        for _ in range(count):
            parts.append(random.choice(vowels))
            if random.random() < 0.5 and len(parts) < count * 2:
                parts.append(random.choice(other))
        # Add trailing consonants
        for _ in range(random.randint(0, 3)):
            parts.append(random.choice(other))
        return ''.join(parts)

    def _generate_word_with_vowel_count_and_last(self, count, last_vowel):
        vowels = ['a', 'e', 'i', 'o', 'u']
        other = [chr(c) for c in range(ord('a'), ord('z')+1) if chr(c) not in vowels]
        parts = []
        # Generate count-1 vowels
        for _ in range(count-1):
            parts.append(random.choice(vowels))
            if random.random() < 0.5:
                parts.append(random.choice(other))
        # Add the last vowel
        parts.append(last_vowel)
        # Add trailing consonants
        for _ in range(random.randint(0, 3)):
            parts.append(random.choice(other))
        return ''.join(parts)
