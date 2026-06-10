import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CsoldierandcardsInstructionGenerator(BaseInstructionGenerator):
    """Csoldierandcards Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Csoldierandcards指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = params.get('min_n', 2)
        self.max_n = params.get('max_n', 10)
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        cards = list(range(1, n+1))
        random.shuffle(cards)
        k1 = random.randint(1, n-1)
        return {
            'n': n,
            'player1': cards[:k1],
            'player2': cards[k1:]
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        prompt = f"""Two soldiers are playing a card war game. The deck has {question_case['n']} unique cards numbered 1 to {question_case['n']}. 

Soldier 1 has {len(question_case['player1'])} cards (top to bottom): {', '.join(map(str, question_case['player1']))}.
Soldier 2 has {len(question_case['player2'])} cards (top to bottom): {', '.join(map(str, question_case['player2']))}.

Rules:
1. Each fight: Both play their top card. Higher value wins.
2. Winner takes both cards (opponent's first, then theirs) to their deck's bottom.
3. Game ends when a soldier has no cards. If a state repeats, the game loops infinitely.

You must output either:
- The number of fights and the winner (e.g., [answer]6 2[/answer])
- Or [answer]-1[/answer] if it never ends.

Use exact format with [answer] tags."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

