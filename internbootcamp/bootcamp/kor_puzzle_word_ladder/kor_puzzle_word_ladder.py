"""### 谜题描述
1.The game starts with a word and specifies an ending word.
2.Only one letter can be changed at a time, and each intermediate step must be a valid word.
3.Change from the start word to the end word by the fewest steps.
4.The question will give the start and end words, answer the minimum number of steps needed to change from the start word to the end word.Example questions are as follows:

<example 0>
From \"MOM\" to \"DAD\".
Output the number in double brackets. For example, if it takes 3 steps from the start word to the end word, present the answer as [[3]].
</example 0>

<example 1>
From \"TEA\" to \"POT\".
Output the number in double brackets. For example, if it takes 3 steps from the start word to the end word, present the answer as [[3]].
</example 1>

<example 2>
From \"FLY\" to \"CRY\".
Output the number in double brackets. For example, if it takes 3 steps from the start word to the end word, present the answer as [[3]].
</example 2>

<example 3>
From \"WINE\" to \"BARE\".
Output the number in double brackets. For example, if it takes 3 steps from the start word to the end word, present the answer as [[3]].
</example 3>

<example 4>
From \"COLD\" to \"WARM\".
Output the number in double brackets. For example, if it takes 3 steps from the start word to the end word, present the answer as [[3]].
</example 4>

<example 5>
From \"LOST\" to \"HERE\".
Output the number in double brackets. For example, if it takes 3 steps from the start word to the end word, present the answer as [[3]].
</example 5>

<example 6>
From \"SAME\" to \"COST\".
Output the number in double brackets. For example, if it takes 3 steps from the start word to the end word, present the answer as [[3]].
</example 6>

<example 7>
From \"HEAD\" to \"TALE\".
Output the number in double brackets. For example, if it takes 3 steps from the start word to the end word, present the answer as [[3]].
</example 7>

<example 8>
From \"COAL\" to \"COAT\".
Output the number in double brackets. For example, if it takes 3 steps from the start word to the end word, present the answer as [[3]].
</example 8>

<example 9>
From \"POOR\" to \"RICH\".
Output the number in double brackets. For example, if it takes 3 steps from the start word to the end word, present the answer as [[3]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
from collections import defaultdict, deque
import random
import re
# from nltk.corpus import words
from bootcamp import Basebootcamp

class KorPuzzleWordLadderbootcamp(Basebootcamp):
    def __init__(self, **params):
        super().__init__(**params)
        self.word_length = params.get('word_length', 3)
        self.word_list = self._load_words(self.word_length)
        self.word_set = set(self.word_list)
        self.adjacency = self._build_adjacency()
    
    def _load_words(self, length):
        words_file = "/".join(__file__.split('/')[:-4]) + "/" + "internbootcamp/libs/data/words_alpha_370000.txt"
        with open(words_file, 'r') as f:
            words = f.readlines()
            words = [w.strip() for w in words]
        word_list =  [word.lower() for word in words if word.isalpha() and len(word) == length]
        # try:
            # word_list = [word.lower() for word in words.words() 
            #             if word.isalpha() and len(word) == length]
        # except LookupError:
        #     import nltk
        #     nltk.download('words')
        #     word_list = [word.lower() for word in words.words() 
        #                 if word.isalpha() and len(word) == length]
        return word_list
    
    def _build_adjacency(self):
        adjacency = defaultdict(list)
        for word in self.word_list:
            for i in range(len(word)):
                original_char = word[i]
                for c in 'abcdefghijklmnopqrstuvwxyz':
                    if c == original_char:
                        continue
                    candidate = word[:i] + c + word[i+1:]
                    if candidate in self.word_set:
                        adjacency[word].append(candidate)
        return adjacency
    
    def case_generator(self):
        max_attempts = 100
        for _ in range(max_attempts):
            start = random.choice(self.word_list)
            end = random.choice(self.word_list)
            if start == end:
                continue
            steps = self._bfs(start, end)
            if steps is not None:
                return {
                    'start_word': start,
                    'end_word': end,
                    'correct_steps': steps
                }
        # Fallback to a known example
        return {
            'start_word': 'mom',
            'end_word': 'dad',
            'correct_steps': 3
        }
    
    def _bfs(self, start, end):
        if start not in self.adjacency or end not in self.adjacency:
            return None
        if start == end:
            return 0
        visited = set()
        queue = deque([(start, 0)])
        visited.add(start)
        while queue:
            current_word, steps = queue.popleft()
            for neighbor in self.adjacency[current_word]:
                if neighbor == end:
                    return steps + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, steps + 1))
        return None
    
    @staticmethod
    def prompt_func(question_case) -> str:
        start = question_case['start_word'].upper()
        end = question_case['end_word'].upper()
        prompt = (
            f"You are trying to solve a word ladder puzzle. The goal is to transform the start word into the end word by changing one letter at a time, with each intermediate step forming a valid English word. Your task is to determine the minimum number of steps required.\n\n"
            f"Start word: {start}\n"
            f"End word: {end}\n\n"
            "Rules:\n"
            "1. You can change only one letter in each step.\n"
            "2. All intermediate words formed must be valid English words.\n"
            "3. The answer should be the minimum number of steps needed.\n\n"
            "Please provide your answer inside double square brackets. For example, if the answer is 3, your response should be: [[3]]\n"
        )
        return prompt
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(\d+)\]\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_steps']
