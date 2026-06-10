import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import Counter
from itertools import permutations




class KorpuzzleconnectwordsInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzleconnectwords Bootcamp指令生成器"""
    
    def __init__(self, word_pool=None):
        """
        初始化Korpuzzleconnectwords指令生成器
        
        Args:
            word_pool: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.word_pool = word_pool or self.default_word_pool()
    
    def case_generator(self):
        # 动态生成有效案例（保证有解）
        while True:
            # 随机选择单词数量（1-5）
            num_words = random.randint(1, 3)
            
            # 随机选择单词长度组合
            possible_lengths = [k for k in self.word_pool.keys() 
                               if k * num_words <= 7]  # 控制总字母数
            if not possible_lengths:
                continue
            target_lengths = random.choice([
                random.choices(possible_lengths, k=num_words)
            ])
            
            # 生成有效单词组合
            valid_combination = self.find_valid_combination(target_lengths)
            if valid_combination:
                all_letters = list(''.join(valid_combination))
                return {
                    'letters': sorted(all_letters),
                    'word_lengths': target_lengths,
                    'solution': valid_combination
                }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        letters = ' '.join(question_case['letters'])
        word_lengths = question_case['word_lengths']
        words_desc = ', '.join([f'{l} letter' for l in word_lengths])
        
        prompt = f"""Given letters: {letters}
Form {len(word_lengths)} words with lengths: {words_desc}

Rules:
1. Use each letter exactly once
2. No letter repetition in words
3. Order matters for word lengths
4. Valid English words only

Answer format: [[space-separated-words]]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def default_word_pool():
        return {
            2: {'BE', 'NO', 'IN', 'TO', 'UP'},
            3: {'CAT', 'DOG', 'BED', 'PEN', 'CAR', 'BAT', 'RAT', 'MAT', 'PAN'},
            4: {'DESK', 'BALL', 'FISH', 'CAKE', 'ROAD', 'BEAN', 'UNIT'},
            5: {'APPLE', 'TABLE', 'CHAIR'}
        }

    def find_valid_combination(self, lengths):
        # 确保所有单词存在并共享字母
        for _ in range(100):  # 防止无限循环
            candidate = []
            used_letters = []
            for length in lengths:
                valid_words = [w for w in self.word_pool.get(length, [])
                              if not set(w).intersection(used_letters)]
                if not valid_words:
                    break
                word = random.choice(valid_words)
                candidate.append(word)
                used_letters.extend(list(word))
            if len(candidate) == len(lengths):
                return candidate
        return None
