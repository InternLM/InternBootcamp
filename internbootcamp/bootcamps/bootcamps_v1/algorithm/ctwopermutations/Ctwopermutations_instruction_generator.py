import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CtwopermutationsInstructionGenerator(BaseInstructionGenerator):
    """Ctwopermutations Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, max_m=5):
        """
        初始化Ctwopermutations指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        p = list(range(1, n+1))
        random.shuffle(p)
        q = list(range(1, n+1))
        random.shuffle(q)
        m = random.randint(1, self.max_m)
        queries = []
        for _ in range(m):
            a = random.randint(1, n)
            b = random.randint(1, n)
            c = random.randint(1, n)
            d = random.randint(1, n)
            queries.append((a, b, c, d))
        answers = self.calculate_answers(n, p, q, queries)
        return {
            'n': n,
            'p': p,
            'q': q,
            'm': m,
            'queries': queries,
            'answers': answers
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        p = ' '.join(map(str, question_case['p']))
        q = ' '.join(map(str, question_case['q']))
        m = question_case['m']
        queries = '\n'.join(' '.join(map(str, q)) for q in question_case['queries'])
        prompt = f"""给定两个长度为{n}的排列p和q，处理{m}个查询。每个查询给出参数a,b,c,d，根据以下规则计算：

1. 首个查询x=0，之后x=前一个查询结果
2. 计算f(z)=((z-1 + x) mod n) +1
3. l1=min(f(a),f(b)), r1=max(f(a),f(b))
4. l2=min(f(c),f(d)), r2=max(f(c),f(d))
5. 统计同时满足以下条件的整数v的数量：
   - v在p中的位置位于[l1, r1]区间
   - v在q中的位置位于[l2, r2]区间

输入数据格式：
{n}
{p}
{q}
{m}
{queries}

要求输出每个查询的结果，每个答案单独一行，包裹在[answer]标签内。如：
[answer]
3
0
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_answers(n, p, q, queries):
        pos_p = {v: i+1 for i, v in enumerate(p)}
        pos_q = {v: i+1 for i, v in enumerate(q)}
        x = 0
        answers = []
        for a, b, c, d in queries:
            fa = ((a - 1 + x) % n) + 1
            fb = ((b - 1 + x) % n) + 1
            fc = ((c - 1 + x) % n) + 1
            fd = ((d - 1 + x) % n) + 1
            l1, r1 = sorted([fa, fb])
            l2, r2 = sorted([fc, fd])

            valid_p = {v for v in range(1, n+1) if l1 <= pos_p[v] <= r1}
            valid_q = {v for v in range(1, n+1) if l2 <= pos_q[v] <= r2}
            count = len(valid_p & valid_q)

            answers.append(count)
            x = count
        return answers
