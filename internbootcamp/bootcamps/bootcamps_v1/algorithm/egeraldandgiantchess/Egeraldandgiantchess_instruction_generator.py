import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re

# === 源文件中的全局变量 ===

global_fac = [1]

global_inv = [1]

mod_value = 10**9 + 7



# === 源文件中的全局函数 ===

def init_global_fac_inv(maxn):
    global global_fac, global_inv, mod_value
    if maxn < len(global_fac):
        return
    current_len = len(global_fac)
    for i in range(current_len, maxn + 1):
        global_fac.append((global_fac[-1] * i) % mod_value)
        inv_i = pow(i, mod_value - 2, mod_value)
        new_inv = (global_inv[-1] * inv_i) % mod_value
        global_inv.append(new_inv)

def culC(a, b):
    if a < 0 or b < 0 or a < b:
        return 0
    init_global_fac_inv(a)
    return global_fac[a] * global_inv[b] % mod_value * global_inv[a - b] % mod_value

def path(sx, sy, tx, ty):
    dx = tx - sx
    dy = ty - sy
    if dx < 0 or dy < 0:
        return 0
    return culC(dx + dy, dx)

def compute_solution(h, w, blocks):
    mod = 10**9 + 7
    blocks_sorted = sorted(blocks, key=lambda x: (x[0], x[1]))
    blocks_sorted.append((h, w))
    n = len(blocks_sorted)
    dp = [0] * n

    for i in range(n):
        r, c = blocks_sorted[i]
        total = path(1, 1, r, c)
        for j in range(i):
            pr, pc = blocks_sorted[j]
            if pr <= r and pc <= c:
                ways = path(pr, pc, r, c) * dp[j]
                total = (total - ways) % mod
        dp[i] = total % mod
    return dp[-1]


class EgeraldandgiantchessInstructionGenerator(BaseInstructionGenerator):
    """Egeraldandgiantchess Bootcamp指令生成器"""
    
    def __init__(self, h_range=(1, 100), w_range=(1, 100), n_max=2000):
        """
        初始化Egeraldandgiantchess指令生成器
        
        Args:
            h_range: 参数描述
            w_range: 参数描述
            n_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.h_range = h_range
        self.w_range = w_range
        self.n_max = n_max
    
    def case_generator(self):
        import random
        while True:
            h = random.randint(self.h_range[0], self.h_range[1])
            w = random.randint(self.w_range[0], self.w_range[1])
            if h * w >= 3:
                break
        
        max_black = h * w - 2
        n = random.randint(1, min(self.n_max, max_black))
        
        available = []
        for r in range(1, h + 1):
            for c in range(1, w + 1):
                if (r, c) != (1, 1) and (r, c) != (h, w):
                    available.append((r, c))
        
        selected = random.sample(available, n)
        selected_sorted = sorted(selected, key=lambda x: (x[0], x[1]))
        
        correct_answer = compute_solution(h, w, selected_sorted)
        
        return {
            'h': h,
            'w': w,
            'n': n,
            'black_cells': selected_sorted,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        h = question_case['h']
        w = question_case['w']
        n = question_case['n']
        black_cells = question_case['black_cells']
        
        input_lines = [f"{h} {w} {n}"] + [f"{r} {c}" for r, c in black_cells]
        input_str = '\n'.join(input_lines)
        
        example_output = "2"
        
        prompt = f"""You are playing Giant Chess and need to calculate the number of valid paths from the start to the end. The rules are as follows:

- The chessboard is {h} rows (h) by {w} columns (w). 
- Start at the top-left corner (1,1) and end at the bottom-right corner ({h},{w}).
- You can only move right or down one cell at a time.
- Black cells are blocked. The start and end cells are always white.
- Output the number of valid paths modulo 1e9+7.

Input format:
The first line contains three integers h, w, n. The next n lines each contain two integers r and c, representing the position of a black cell.

Given the following input data:

{input_str}

Please compute the correct answer. Ensure your final answer is enclosed within [answer] and [/answer] tags. For example: [answer]{example_output}[/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

