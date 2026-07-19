"""### 谜题描述
1.The puzzle gives a set of letters and the number and length of words to be spelled, e.g. 2 words: 2 letters, 3 letters, 3 letters.
2.The player has to use the given letters to spell a word of the required length and number of letters.
3.Each letter can be used at most once in a word.Example questions are as follows:

<example 0>
P E A 2 words:3 letter,3 letter.
The answers should be given in order,i.e. If the requirement is for 3 words: 2 letter,3 letter,3 letter then a two letter word is given first followed by two three letter words separated by spaces.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 0>

<example 1>
T C A 2 words:3 letter,3 letter.
The answers should be given in order,i.e. If the requirement is for 3 words: 2 letter,3 letter,3 letter then a two letter word is given first followed by two three letter words separated by spaces.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 1>

<example 2>
T R A 7 words: 2 letter,2 letter,2 letter,3 letter,3 letter,3 letter,3 letter.
The answers should be given in order,i.e. If the requirement is for 3 words: 2 letter,3 letter,3 letter then a two letter word is given first followed by two three letter words separated by spaces.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 2>

<example 3>
N D K I 7 words: 3 letter,3 letter,3 letter,3 letter,3 letter,4 letter,4 letter.
The answers should be given in order,i.e. If the requirement is for 3 words: 2 letter,3 letter,3 letter then a two letter word is given first followed by two three letter words separated by spaces.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 3>

<example 4>
A E B T 4 words: 4 letter,4 letter,4 letter,4 letter.
The answers should be given in order,i.e. If the requirement is for 3 words: 2 letter,3 letter,3 letter then a two letter word is given first followed by two three letter words separated by spaces.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 4>

<example 5>
T I E D 5 words: 4 letter,4 letter,4 letter,4 letter,4 letter.
The answers should be given in order,i.e. If the requirement is for 3 words: 2 letter,3 letter,3 letter then a two letter word is given first followed by two three letter words separated by spaces.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 5>

<example 6>
N E M A 5 words: 4 letter,4 letter,4 letter,4 letter.
The answers should be given in order,i.e. If the requirement is for 3 words: 2 letter,3 letter,3 letter then a two letter word is given first followed by two three letter words separated by spaces.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 6>

<example 7>
B D E N 5 words: 2 letter,4 letter.
The answers should be given in order,i.e. If the requirement is for 3 words: 2 letter,3 letter,3 letter then a two letter word is given first followed by two three letter words separated by spaces.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 7>

<example 8>
U N T A 3 words: 4 letter,4 letter,4 letter.
The answers should be given in order,i.e. If the requirement is for 3 words: 2 letter,3 letter,3 letter then a two letter word is given first followed by two three letter words separated by spaces.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 8>

<example 9>
O B W L 6 words: 3 letter, 3 letter,3 letter,3 letter,4 letter,4 letter.
The answers should be given in order,i.e. If the requirement is for 3 words: 2 letter,3 letter,3 letter then a two letter word is given first followed by two three letter words separated by spaces.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from internbootcamp.bootcamp import Basebootcamp
import random
import re
from collections import Counter
from itertools import permutations

class KorPuzzleConnectWordsbootcamp(Basebootcamp):
    def __init__(self, word_pool=None):
        self.word_pool = word_pool or self.default_word_pool()
        
    @staticmethod
    def default_word_pool():
        return {
            2: {'BE', 'NO', 'IN', 'TO', 'UP'},
            3: {'CAT', 'DOG', 'BED', 'PEN', 'CAR', 'BAT', 'RAT', 'MAT', 'PAN'},
            4: {'DESK', 'BALL', 'FISH', 'CAKE', 'ROAD', 'BEAN', 'UNIT'},
            5: {'APPLE', 'TABLE', 'CHAIR'}
        }

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

if __name__ == '__main__':
    while True:
        bootcamp_cls = KorPuzzleConnectWordsbootcamp
        bootcamp = KorPuzzleConnectWordsbootcamp()
        case = bootcamp.case_generator()
        while True:
            print('='*50, 'case', '='*50 + '\n', case, '\n' ,'='*50, 'case', '='*50)
            print('='*50, bootcamp_cls.__name__, '='*50 + '\n', bootcamp_cls.prompt_func(case),'\n' +'='*50, bootcamp_cls.__name__, '='*50)
            input_answer = input('Enter your answer: ')
            print('提取到的答案：', bootcamp_cls.extract_output(input_answer), '\n')
            print('你的答案得分：', bootcamp_cls.verify_score(input_answer, case,short_penalty=False, format_penalty=False))
            exit_or_not = input('是否退出？(y/n)')
            if exit_or_not == 'y':
                break