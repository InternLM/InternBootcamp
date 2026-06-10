import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import random
import re




class Koroperationunicode203bRewardCalculator(BaseRewardCalculator):
    """Koroperationunicode203b奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        if not matches:
            return None
        last_match = matches[-1].strip()
        # 清理多余内容
        cleaned = re.sub(r'[^0-9or]', '', last_match.lower())
        return cleaned if cleaned else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        
        try:
            if identity['type'] == 'compute':
                return int(solution) == identity['answer']
            
            elif identity['type'] == 'solve_x':
                # 处理多格式输入
                parts = re.split(r'\bor\b|,', solution)
                answers = set()
                for p in parts:
                    p = p.strip()
                    if p.isdigit():
                        answers.add(int(p))
                return answers == set(identity['solutions'])
            
            elif identity['type'] == 'solve_c':
                return int(solution) == identity['answer']
            
            return False
        except Exception as e:
            return False
    
    # 其他额外方法

