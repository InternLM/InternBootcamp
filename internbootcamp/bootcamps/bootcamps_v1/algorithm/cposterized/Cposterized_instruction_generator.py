import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def generate_answer(n, k, p):
    assigned = [0] * 256
    key = list(range(256))
    ans = [0] * n

    for i in range(n):
        cur = p[i]
        if assigned[cur]:
            ans[i] = key[cur]
            continue

        foundkey = False
        no1 = True
        rep = -1
        repb = -1
        start_search = max(0, cur - k + 1)
        
        # 扫描可能的区间
        for it in range(cur, start_search - 1, -1):
            if assigned[it]:
                no1 = False
                if key[it] == it:  # 有效锚点
                    foundkey = True
                    rep = it
                    break
            elif no1:
                repb = it

        if not foundkey:
            # 处理255边界
            group_start = max(0, repb)
            group_end = min(255, group_start + k - 1)
            for it in range(group_start, group_end + 1):
                assigned[it] = 1
                key[it] = group_start
            ans[i] = group_start
        else:
            group_end = min(255, rep + k - 1)
            for it in range(rep, group_end + 1):
                assigned[it] = 1
                key[it] = rep
            ans[i] = rep

    return ans


class CposterizedInstructionGenerator(BaseInstructionGenerator):
    """Cposterized Bootcamp指令生成器"""
    
    def __init__(self, max_n=10**5, min_n=1, max_k=256, min_k=1):
        """
        初始化Cposterized指令生成器
        
        Args:
            max_n: 参数描述
            min_n: 参数描述
            max_k: 参数描述
            min_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.min_n = min_n
        self.max_k = max_k
        self.min_k = min_k
    
    def case_generator(self):
        # 生成关键测试模式
        if random.random() < 0.2:
            # 模式1：全范围测试 (k=256)
            n = random.randint(100, 1000)
            k = 256
            p = [random.randint(0, 255) for _ in range(n)]
        elif random.random() < 0.3:
            # 模式2：最小k测试 (k=1)
            n = random.randint(1, 1000)
            k = 1
            p = [random.randint(0, 255) for _ in range(n)]
        else:
            # 常规随机测试
            n = random.randint(self.min_n, self.max_n)
            k = random.randint(self.min_k, min(self.max_k, 256))
            p = [random.randint(0, 255) for _ in range(n)]
        
        # 强制包含边界值
        if n >= 2:
            p[0] = 0
            p[-1] = 255
        
        ans = generate_answer(n, k, p)
        return {
            'n': n,
            'k': k,
            'p': p,
            'ans': ans
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = f"{question_case['n']} {question_case['k']}\n{' '.join(map(str, question_case['p']))}"
        prompt = f"""Implement the posterization filter to produce the lexicographically smallest array.

**Key Rules:**
1. Groups must be consecutive colors with size ≤ {question_case['k']}
2. Each group selects ONE key color within its range
3. ALL occurrences of colors in a group are replaced by the key
4. The result array must be the lex smallest possible when comparing element-wise from left to right

**Input:**
{input_lines}

**Output Format:**
Exactly {question_case['n']} integers between [answer] and [/answer], e.g.:
[answer]0 1 2 3[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

