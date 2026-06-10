import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
import bisect
from collections import defaultdict




class ErooksandrectanglesRewardCalculator(BaseRewardCalculator):
    """Erooksandrectangles奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        answer_block = matches[-1].strip()
        answers = []
        for line in answer_block.split('\n'):
            line = line.strip().upper()
            if line in ('YES', 'NO'):
                answers.append(line)
            elif line:
                return None
        return '\n'.join(answers) if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # Preprocess rook positions into column and row maps
        columns = defaultdict(list)
        rows = defaultdict(list)
        for x, y in identity['rooks']:
            bisect.insort(columns[y], x)
            bisect.insort(rows[x], y)
        
        correct = []
        for q in identity['queries']:
            x1, y1, x2, y2 = q['x1'], q['y1'], q['x2'], q['y2']
            valid = True
            
            # Check condition 1: All columns in [y1,y2] have a rook in [x1,x2]
            cond1 = True
            for y in range(y1, y2 + 1):
                if y not in columns:
                    cond1 = False
                    break
                # Find if any x in column y is within [x1,x2]
                idx = bisect.bisect_left(columns[y], x1)
                if idx < len(columns[y]) and columns[y][idx] <= x2:
                    continue
                else:
                    cond1 = False
                    break
            if cond1:
                correct.append("YES")
                continue
            
            # Check condition 2: All rows in [x1,x2] have a rook in [y1,y2]
            cond2 = True
            for x in range(x1, x2 + 1):
                if x not in rows:
                    cond2 = False
                    break
                # Find if any y in row x is within [y1,y2]
                idx = bisect.bisect_left(rows[x], y1)
                if idx < len(rows[x]) and rows[x][idx] <= y2:
                    continue
                else:
                    cond2 = False
                    break
            correct.append("YES" if cond2 else "NO")
        
        user_answers = solution.split('\n') if solution else []
        return len(user_answers) == len(correct) and all(u == c for u, c in zip(user_answers, correct))
    
    # 其他额外方法

