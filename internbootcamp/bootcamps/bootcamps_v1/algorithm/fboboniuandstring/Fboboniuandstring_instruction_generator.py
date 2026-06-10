import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def solve_bn_case(dots):
    n = len(dots)
    l = -1
    r = 10**7
    final_dot = (0, 0)
    while r - l > 1:
        mid = (l + r) // 2
        minx = -10**7
        maxx = 10**7
        miny = -10**7
        maxy = 10**7
        minXY = -10**7
        maxXY = 10**7
        
        for x, y in dots:
            minx = max(minx, x - mid)
            maxx = min(maxx, x + mid)
            miny = max(miny, y - mid)
            maxy = min(maxy, y + mid)
            minXY = max(minXY, (x - y) - mid)
            maxXY = min(maxXY, (x - y) + mid)
        
        may_be = (minx <= maxx) and (miny <= maxy) and (minXY <= maxXY)
        if may_be:
            lower_bound = minx - maxy
            upper_bound = maxx - miny
            if lower_bound > maxXY or upper_bound < minXY:
                may_be = False
        
        if may_be:
            x_t = minx
            y_t = maxy
            if (x_t - y_t) < minXY:
                move = min(maxx - x_t, minXY - (x_t - y_t))
                x_t += move
                if (x_t - y_t) < minXY:
                    move = min(y_t - miny, minXY - (x_t - y_t))
                    y_t -= move
            x_t = max(x_t, 0)
            y_t = max(y_t, 0)
            if x_t == 0 and y_t == 0:
                x_t = 1
                y_t = 0
            final_dot = (x_t, y_t)
            r = mid
        else:
            l = mid
    return r, final_dot


class FboboniuandstringInstructionGenerator(BaseInstructionGenerator):
    """Fboboniuandstring Bootcamp指令生成器"""
    
    def __init__(self, n=3, max_b=5, max_n=5):
        """
        初始化Fboboniuandstring指令生成器
        
        Args:
            n: 参数描述
            max_b: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.max_b = max_b
        self.max_n = max_n
    
    def case_generator(self):
        dots = []
        for _ in range(self.n):
            x = random.randint(0, self.max_b)
            y = random.randint(0, self.max_n)
            while x + y == 0:
                x = random.randint(0, self.max_b)
                y = random.randint(0, self.max_n)
            dots.append((x, y))
        correct_d_max, (t_x, t_y) = solve_bn_case(dots)
        strings = []
        for x, y in dots:
            strings.append('B' * x + 'N' * y)
        return {
            'n': self.n,
            'strings': strings,
            'dots': dots,
            'correct_d_max': correct_d_max
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [str(question_case['n'])] + question_case['strings']
        input_part = '\n'.join(input_lines)
        prompt = f"""You need to solve a BN-string optimization problem. Find a non-empty BN-string t such that the maximum distance to given strings is minimized. 

**Problem Details:**
- Distance 'dist(s, t)' is the minimum operations to make s similar to t, where similarity requires equal length and possible permutation of characters.
- Operations include adding/removing characters or substrings "BN"/"NB".

**Input:**
{input_part}

**Output Format:**
First line: the minimal maximum distance.
Second line: the optimal BN-string t.

Put your answer within [answer] and [/answer] tags. Example:
[answer]
3
BNNBB
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

