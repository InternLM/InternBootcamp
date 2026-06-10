import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CyuhaoandaparenthesisRewardCalculator(BaseRewardCalculator):
    """Cyuhaoandaparenthesis奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 引用题目给出的参考算法进行验证
        def process(s):
            stack = []
            for c in s:
                if c == ")":
                    if stack and stack[-1] == "(":
                        stack.pop()
                        continue
                stack.append(c)
            if not stack: return 0, True
            has_open = '(' in stack
            has_close = ')' in stack
            if has_open and has_close: return 0, False
            return len(stack) if has_open else -len(stack), True

        opening = []
        closing = []
        balanced = 0
        
        for s in identity['sequences']:
            score, valid = process(s)
            if not valid: continue
            if score == 0:
                balanced += 1
            elif score > 0:
                opening.append(score)
            else:
                closing.append(-score)
        
        # 匹配开闭序列
        opening.sort()
        closing.sort()
        pairs = 0
        i = j = 0
        while i < len(opening) and j < len(closing):
            if opening[i] == closing[j]:
                pairs += 1
                i += 1
                j += 1
            elif opening[i] < closing[j]:
                i += 1
            else:
                j += 1
        
        return solution == (pairs + balanced // 2)
    
    # 其他额外方法

