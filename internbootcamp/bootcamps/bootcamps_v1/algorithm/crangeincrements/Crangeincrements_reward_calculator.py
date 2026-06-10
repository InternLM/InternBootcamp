import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def solve(a_list):
    n = len(a_list)
    l = a_list.copy()
    ans = []
    s = []
    opened = []
    for i in range(n):
        current = l[i]
        if not s or current > s[-1]:
            s.append(current)
            opened.append(i + 1)
        elif current < s[-1]:
            while s and current < s[-1]:
                pp = True
                base = current
                if len(s) > 1:
                    base = max(base, s[-2])
                if base == current:
                    pp = False
                val = s[-1] - base
                while val > 0:
                    ans.append(f"{opened[-1]} {i}")
                    val -= 1
                if pp:
                    s.pop()
                    opened.pop()
                else:
                    break
            if s:
                s[-1] = current
    while s:
        base = 0
        if len(s) > 1:
            base = s[-2]
        val = s[-1] - base
        while val > 0:
            ans.append(f"{opened[-1]} {n}")
            val -= 1
        s.pop()
        opened.pop()
    operations = []
    for op in ans:
        li, ri = map(int, op.split())
        operations.append((li, ri))
    return operations


class CrangeincrementsRewardCalculator(BaseRewardCalculator):
    """Crangeincrements奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_block = answer_blocks[-1].strip()
        lines = [line.strip() for line in last_block.split('\n') if line.strip()]
        if len(lines) < 1:
            return None
        try:
            t = int(lines[0])
            if len(lines) != t + 1:
                return None
            operations = []
            for line in lines[1:t+1]:  # 防止多余行干扰
                parts = line.split()
                if len(parts) != 2:
                    return None
                l = int(parts[0])
                r = int(parts[1])
                operations.append( (l, r) )
            return operations
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        # 检查操作次数是否匹配最优解
        if len(solution) != identity['correct_t']:
            return False
        n = identity['n']
        a = identity['a']
        # 模拟操作过程
        simulated = [0] * n
        for l, r in solution:
            if l < 1 or r > n or l > r:  # 参数合法性检查
                return False
            start = l - 1
            end = r - 1
            for i in range(start, end + 1):
                simulated[i] += 1
        return simulated == a
    
    # 其他额外方法

