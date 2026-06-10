import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict
from io import StringIO
import sys

# === 源文件中的全局函数 ===

def solve(input_str):
    # 保持原解题逻辑不变，确保正确性
    from collections import defaultdict

    sys.stdin = StringIO(input_str)
    old_stdout = sys.stdout
    sys.stdout = output = StringIO()

    try:
        n, m = map(int, sys.stdin.readline().split())
        b, inc, d = map(int, sys.stdin.readline().split())
        dat = list(map(int, sys.stdin.read().split()))
        j = n * 3
        ev = [[] for _ in range(n)]
        a = defaultdict(int)
        for _ in range(m):
            t = dat[j]
            i = dat[j+1]
            h = dat[j+2]
            ev[i-1].append((t, h))
            j += 3
        j = 0
        c = 0
        infinite_flag = False
        for i in range(n):
            mh = dat[j]
            sh = dat[j+1]
            reg = dat[j+2]
            ev[i].sort()
            h = sh
            p = 0
            on = (h <= d)
            if on:
                c += 1
            if reg > 0:
                if mh <= d and inc > 0:
                    infinite_flag = True
                    break
                for (t, nh) in ev[i]:
                    if on:
                        if (d - h) < 0:
                            x = p + ((d - h) // reg) + 1
                        else:
                            x = p + (d - h) // reg + 1
                        if x < t:
                            a[x] -= 1
                            on = False
                    non = (nh <= d)
                    if on != non:
                        a[t] += 1 if non else -1
                    on = non
                    p = t
                    h = nh
                if on:
                    x = p + (d - h) // reg + 1
                    a[x] -= 1
            else:
                if on and inc > 0:
                    infinite_flag = True
                    break
                for (t, nh) in ev[i]:
                    non = nh <= d
                    if on != non:
                        a[t] += 1 if non else -1
                    on = non
                    p = t
            j += 3
        if infinite_flag:
            print(-1)
        else:
            ans = c * b
            sorted_times = sorted(a.keys())
            for t in sorted_times:
                y = c * (b + (t - 1) * inc)
                if ans < y:
                    ans = y
                c += a[t]
            print(ans)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sys.stdout = old_stdout
    return output.getvalue().strip()


class CperunultRewardCalculator(BaseRewardCalculator):
    """Cperunult奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(-?\d+)\s*\[/answer\]', output, re.IGNORECASE)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 构造输入字符串
        input_lines = [
            f"{identity['n']} {identity['m']}",
            f"{identity['b']} {identity['inc']} {identity['d']}"
        ]
        
        for enemy in identity['enemies']:
            input_lines.append(f"{enemy['h']} {enemy['sh']} {enemy['r']}")
        
        for event in identity['events']:
            input_lines.append(f"{event['t']} {event['e']} {event['h']}")
        
        try:
            correct = solve('\n'.join(input_lines))
            return str(solution) == correct
        except:
            return False
    
    # 其他额外方法

