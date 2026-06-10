import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class KorpuzzlewordrootsandaffixesInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzlewordrootsandaffixes Bootcamp指令生成器"""
    
    def __init__(self, affix_type='random', min_segments=3, max_segments=5):
        """
        初始化Korpuzzlewordrootsandaffixes指令生成器
        
        Args:
            affix_type: 参数描述
            min_segments: 参数描述
            max_segments: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if affix_type not in ['prefix', 'suffix', 'random']:
            raise ValueError("affix_type must be 'prefix', 'suffix', or 'random'")
        self.affix_type = affix_type
        self.min_segments = min_segments
        self.max_segments = max_segments
        if min_segments < 2 or min_segments > max_segments:
            raise ValueError("Invalid segment range")
    
    def case_generator(self):
        affix_type = self.affix_type
        if affix_type == 'random':
            affix_type = random.choice(['prefix', 'suffix'])
        
        candidates = [entry for entry in self.AFFIX_DATA[affix_type] if len(entry['segments']) >= self.min_segments]
        if not candidates:
            raise ValueError("No valid entries available")
        
        entry = random.choice(candidates)
        num_segments = random.randint(self.min_segments, min(self.max_segments, len(entry['segments'])))
        selected = random.sample(entry['segments'], num_segments)
        
        return {
            'affix_type': affix_type,
            'affix': entry['affix'],
            'segments': selected
        }
    
    @staticmethod
    def prompt_func(question_case):
        affix_type = question_case['affix_type']
        segments = ", ".join(question_case['segments'])
        return (
            f"You are a linguistic puzzle solver. Add a common {affix_type} to these letter combinations: {segments}.\n"
            f"Rules: Add the same {affix_type} {'before' if affix_type == 'prefix' else 'after'} each segment to form valid words. "
            "Provide your answer within [[double brackets]]. Example: [[answer]]\n"
            f"Question: Add a common {affix_type} to: {segments}."
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

