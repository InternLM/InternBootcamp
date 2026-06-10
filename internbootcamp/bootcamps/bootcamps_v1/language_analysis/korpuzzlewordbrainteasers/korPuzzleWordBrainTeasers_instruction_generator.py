import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class KorpuzzlewordbrainteasersInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzlewordbrainteasers Bootcamp指令生成器"""
    
    def __init__(self, num_words=5, nouns=None):
        """
        初始化Korpuzzlewordbrainteasers指令生成器
        
        Args:
            num_words: 参数描述
            nouns: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.num_words = num_words
        default_nouns = [
            'sun', 'flower', 'pine', 'apple', 'butter', 'fly',
            'news', 'paper', 'cat', 'fish', 'history', 'building',
            'ball', 'room', 'fire', 'place', 'water', 'fall',
            'door', 'knob', 'light', 'house', 'tooth', 'paste',
            'book', 'case', 'cup', 'board', 'air', 'port',
            'rail', 'road', 'sea', 'shell', 'snow', 'ball'
        ]  # 扩展默认名词列表
        self.nouns = nouns if nouns is not None else default_nouns.copy()
        if len(self.nouns) < 4:  # 增强参数校验
            raise ValueError("At least four nouns are required to generate unambiguous compounds")
    
    def case_generator(self):
        words = []
        components = []
        max_attempts = 10000
        attempts = 0
        
        while len(words) < self.num_words:
            noun1 = random.choice(self.nouns)
            noun2 = random.choice(self.nouns)
            combined = noun1 + noun2
            
            # 唯一性校验
            if combined in [w for w, _ in words]:
                attempts += 1
                continue
                
            # 歧义性校验
            if self._has_ambiguous_decomposition(combined, noun1, noun2):
                attempts += 1
                continue
                
            words.append((combined, (noun1, noun2)))
            attempts = 0  # 重置尝试计数器
            
            if attempts > max_attempts:
                raise RuntimeError(f"Failed to generate {self.num_words} valid compounds after {max_attempts} attempts")

        # 打乱顺序避免模式泄露
        random.shuffle(words)
        return {
            'words': [w[0] for w in words],
            'components': [w[1] for w in words]
        }
    
    @staticmethod
    def prompt_func(question_case):
        words = question_case['words']
        words_str = ' '.join([f'"{w}"' for w in words])
        return (
            f'Analyze these compound words: {words_str}\n\n'
            '**Task Requirements:**\n'
            '1. Each word is formed by combining TWO complete nouns\n'
            '2. Output must preserve the original compounding order\n'
            '3. Separate components with single spaces\n'
            '4. All components must exist as standalone nouns\n\n'
            '**Example:**\n'
            'Input: "sunflower"\n'
            'Valid Output: [[sun flower]]\n'
            'Invalid Output: [[sunflow er]] (er is not a noun)\n\n'
            '**Format:**\n'
            'Place your answer within double square brackets, like:\n'
            '[[noun1 noun2 noun3 noun4...]]'
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _has_ambiguous_decomposition(self, word, original1, original2):
        """检查是否存在其他分解方式"""
        for i in range(1, len(word)):
            part1 = word[:i]
            part2 = word[i:]
            if (part1 in self.nouns and part2 in self.nouns and 
                (part1, part2) != (original1, original2) and
                (part2, part1) != (original1, original2)):
                return True
        return False
