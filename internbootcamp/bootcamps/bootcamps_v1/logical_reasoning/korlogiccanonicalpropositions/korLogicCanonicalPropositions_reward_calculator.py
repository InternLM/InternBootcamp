import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from itertools import permutations




class KorlogiccanonicalpropositionsRewardCalculator(BaseRewardCalculator):
    """Korlogiccanonicalpropositions奖励计算器"""
    
    @staticmethod
    def extract_output(text):
        matches = re.findall(r'\[\[(.*?)\]\]', text, flags=re.DOTALL)
        if matches:
            last_match = matches[-1].strip()
            # 清理可能的换行符
            return last_match.replace('\n', ' ')
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            if identity["type"] == "relationship":
                answers = [ans.strip().upper() for ans in solution.split(';')]
                correct = [cls._rel_type_to_option(r) for r in identity["key"]]
                return answers == correct
            
            elif identity["type"] == "symbolization":
                # 允许逻辑等价的不同顺序
                user_ans = re.sub(r'\s+', '', solution).upper()
                expected = re.sub(r'\s+', '', identity["solution"]).upper()
                
                # 生成所有可能的排列组合
                parts = expected.split('∧')
                permutations_set = {
                    '∧'.join(p).strip() 
                    for p in permutations(parts)
                }
                return user_ans in permutations_set
            
            else:  # formula case
                return str(identity["correct"]) in re.findall(r'\d+', solution)
        
        except Exception as e:
            return False
    
    # 其他额外方法

