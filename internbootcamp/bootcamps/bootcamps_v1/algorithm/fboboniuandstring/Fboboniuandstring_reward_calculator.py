import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class FboboniuandstringRewardCalculator(BaseRewardCalculator):
    """Fboboniuandstring奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        if len(lines) < 2:
            return None
        d_str, t = lines[0], lines[1]
        if not t or any(c not in {'B', 'N'} for c in t):
            return None
        try:
            d = int(d_str)
        except:
            return None
        return {'d': d, 't': t}
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        try:
            user_d = solution['d']
            user_t = solution['t']
        except:
            return False
        if not user_t or any(c not in {'B', 'N'} for c in user_t):
            return False
        x_t = user_t.count('B')
        y_t = user_t.count('N')
        if x_t + y_t == 0:
            return False
        correct_d = identity['correct_d_max']
        max_dist = 0
        for x_i, y_i in identity['dots']:
            dx = abs(x_t - x_i)
            dy = abs(y_t - y_i)
            d_xy = abs((x_t - y_t) - (x_i - y_i))
            current = max(dx, dy, d_xy)
            if current > max_dist:
                max_dist = current
        return max_dist == correct_d and user_d == correct_d
    
    # 其他额外方法

