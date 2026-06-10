import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from io import StringIO
import sys




class DflipthecardsInstructionGenerator(BaseInstructionGenerator):
    """Dflipthecards Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, min_n=1, n=None):
        """
        初始化Dflipthecards指令生成器
        
        Args:
            max_n: 参数描述
            min_n: 参数描述
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        if n is not None:
            self.n = n
        else:
            self.n = random.randint(min_n, max_n)
    
    def case_generator(self):
        """完全随机生成卡片配对，包含合法和非法案例"""
        n = self.n
        numbers = list(range(1, 2 * n + 1))
        random.shuffle(numbers)
        
        # 确保正确配对生成
        cards = []
        used = set()
        for _ in range(n):
            available = list(set(numbers) - used)
            a = random.choice(available)
            available.remove(a)
            b = random.choice(available)
            cards.append((a, b))
            used.update({a, b})
        
        input_str = f"{n}\n" + "\n".join(f"{a} {b}" for a, b in cards)
        expected_output = self.solve(input_str)
        
        return {
            'n': n,
            'cards': cards,
            'expected_output': expected_output
        }
    
    @staticmethod
    def prompt_func(question_case):
        # 保持原有prompt格式
        cards_desc = "\n".join([f"Card {i+1}: Front={a}, Back={b}" for i, (a, b) in enumerate(question_case['cards'])])
        return f"""Given a deck of {question_case['n']} cards with unique numbers (1-{2*question_case['n']}) on both sides. Flip some cards and arrange them to satisfy:
- Front numbers strictly increase
- Back numbers strictly decrease

Cards:
{cards_desc}

Output the minimum flips required or -1 if impossible. Put your final answer within [answer] tags like [answer]3[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve(input_str):
        """改进的验证算法，修正数组越界问题"""
        original_stdin = sys.stdin
        sys.stdin = StringIO(input_str)
        try:
            n = int(sys.stdin.readline())
            a = []
            for _ in range(n):
                x, y = map(int, sys.stdin.readline().split())
                a.append((x, y))

            m = 2 * n  # 正确设置数组大小
            pa = [0] * m
            f = [0] * m
            d = [0] * m

            for x, y in a:
                x -= 1
                y -= 1
                if x >= m or y >= m:  # 添加边界检查
                    return -1
                pa[x] = y
                pa[y] = x
                f[y] = 1

            ans = s = c = tot = 0
            hi, lo = m - 1, 0
            ll = rr = -1
            lr = rl = m

            while tot < n:
                upd = 0
                # 高频错误点修复：添加索引范围检查
                while hi >= max(lr, 0):
                    if hi >= m:  # 防止越界
                        hi = m - 1
                        continue
                    if not d[hi]:
                        if rl < hi or rr > pa[hi]:
                            return -1
                        upd = 1
                        rl, rr = hi, pa[hi]
                        if rl >= m or rr >= m:
                            return -1
                        d[rl] = d[rr] = 1
                        s += f[rl]
                        c += 1
                    hi -= 1

                while lo <= min(rr, m-1):
                    if lo < 0:  # 防止负索引
                        lo = 0
                        continue
                    if not d[lo]:
                        if ll > lo or lr < pa[lo]:
                            return -1
                        upd = 1
                        ll, lr = lo, pa[lo]
                        if ll >= m or lr >= m:
                            return -1
                        d[ll] = d[lr] = 1
                        s += f[ll]
                        c += 1
                    lo += 1

                if not upd:
                    ans += min(s, c - s)
                    tot += c
                    if tot < n:
                        if lo >= m:  # 处理越界情况
                            return -1
                        try:
                            ll, lr = lo, pa[lo]
                        except IndexError:
                            return -1
                        if ll >= m or lr >= m:
                            return -1
                        d[ll] = d[lr] = 1
                        lo += 1
                        s = f[ll]
                        c = 1

            return ans if (ll < rl and lr > rr) else -1
        finally:
            sys.stdin = original_stdin
