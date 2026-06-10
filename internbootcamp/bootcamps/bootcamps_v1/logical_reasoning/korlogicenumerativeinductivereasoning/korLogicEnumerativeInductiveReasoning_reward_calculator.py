import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class KorlogicenumerativeinductivereasoningRewardCalculator(BaseRewardCalculator):
    """Korlogicenumerativeinductivereasoning奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 处理两种题型
        choice_match = re.findall(r'\[\[([AB])\]\]', output)
        if choice_match:
            return choice_match[-1]
        
        symbolic_match = re.search(r'\[\[(.+?);(.+?)\]\]', output)
        if symbolic_match:
            return [symbolic_match.group(1), symbolic_match.group(2)]
        
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if identity['question_type'] == 'choice':
            return solution == identity['type']
        
        # 符号题验证逻辑
        expected_premise = {
            'A': '∧'.join([f'P({e})' for e in identity['sampled']]),
            'B': '∧'.join([f'P({e})' for e in identity['instances']])
        }[identity['type']]
        
        expected_conclusion = {
            'A': f'∀e∈{identity["class"]},P(e)',
            'B': f'P({identity["class"]})'
        }[identity['type']]
        
        return (
            solution[0].replace(' ', '') == expected_premise and
            solution[1].replace(' ', '') == expected_conclusion
        )
    
    # 其他额外方法

