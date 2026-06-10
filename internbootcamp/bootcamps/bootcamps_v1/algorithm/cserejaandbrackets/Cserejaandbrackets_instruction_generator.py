import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import math




class CserejaandbracketsInstructionGenerator(BaseInstructionGenerator):
    """Cserejaandbrackets Bootcamp指令生成器"""
    
    def __init__(self, n=20, m=5):
        """
        初始化Cserejaandbrackets指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数:
            n: 括号序列长度 (默认20，最小值5)
            m: 查询数量 (默认5，最小值1)
        """
        self.n = max(n, 5)  # 保证最小长度
        self.m = max(m, 1)  # 至少1个查询
    
    def case_generator(self):
        # 生成更合理的括号序列（包含平衡和不平衡区域）
        s = []
        stack = []
        positions = list(range(self.n))
        random.shuffle(positions)
        pairs = min(self.n//2, 10)  # 生成至少部分合法对
        
        # 生成基础合法对
        for _ in range(pairs):
            if len(positions) >= 2:
                o = positions.pop()
                c = positions.pop()
                s.extend(['']*(max(o,c)+1 - len(s)))
                s[o] = '('
                s[c] = ')'
        
        # 填充剩余位置
        for i in range(self.n):
            if not s[i]:
                s[i] = random.choice(['(', ')'])
        
        # 平衡调整
        s = ''.join(s)
        balance = 0
        final_s = []
        for c in s:
            if c == '(':
                balance += 1
                final_s.append(c)
            else:
                if balance > 0:
                    balance -= 1
                    final_s.append(c)
                else:
                    final_s.append('(')  # 强制平衡
                    balance += 1
        s = ''.join(final_s)
        
        # 生成多样化的查询区间（包含有效区间和随机区间）
        valid_regions = self.find_valid_regions(s)
        queries = []
        
        # 生成有效区域查询
        for _ in range(min(self.m//2, len(valid_regions))):
            l, r = random.choice(valid_regions)
            li = random.randint(l+1, r+1)  # 1-based
            ri = random.randint(li, r+1)
            queries.append((li, ri))
        
        # 补充边界测试用例
        queries.extend([
            (1, 1),  # 单字符测试
            (1, len(s)),  # 全范围测试
            (max(1, len(s)-3), len(s))  # 尾部测试
        ][:min(3, self.m-len(queries))])
        
        # 补充随机区间
        while len(queries) < self.m:
            li = random.randint(1, self.n)
            ri = random.randint(li, self.n)
            queries.append((li, ri))
        
        random.shuffle(queries)
        return {
            's': s,
            'queries': queries,
            'answers': self.compute_answers(s, queries)
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        s = question_case['s']
        queries = question_case['queries']
        return f"""给定由括号组成的字符串s和m个查询，每个查询指定区间[l, r]，要求计算该区间内最长合法括号子序列的长度。合法括号序列定义为可以正确闭合的括号组合。

输入格式：
s（长度n）
m
l1 r1
...
lm rm

输出格式：
m行，每行对应查询结果

特别注意：
1. 区间是闭区间[li, ri]
2. 输出结果必须为非负整数
3. 答案必须严格按输入顺序输出

当前问题：
s = {s}
m = {len(queries)}
查询区间：
""" + '\n'.join(f"{l} {r}" for l, r in queries) + """

请将最终答案按顺序放置在[answer]标签内，例如：
[answer]
0
4
6
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def find_valid_regions(self, s):
        # 寻找有效括号子序列区域
        stack = []
        valid = []
        max_len = 0
        start = 0
        for i, c in enumerate(s):
            if c == '(':
                stack.append(i)
            else:
                if stack:
                    stack.pop()
                    if not stack:
                        valid.append((start, i))
                    else:
                        valid.append((stack[-1]+1, i))
                else:
                    start = i + 1
        return valid if valid else [(0, len(s)-1)]

    @staticmethod
    def compute_answers(s, queries):
        n = len(s)
        a = [0]*(n+1)
        for i in range(1, n+1):
            a[i] = a[i-1] + (1 if s[i-1] == '(' else -1)

        # 构建Sparse Table
        log_table = [0]*(n+2)
        for i in range(2, n+2):
            log_table[i] = log_table[i//2] + 1

        k_max = log_table[n] + 1 if n > 0 else 0
        st = [[0]*(n+1) for _ in range(k_max)]
        st[0] = a.copy()

        for k in range(1, k_max):
            for i in range(n+1 - (1 << k) + 1):
                st[k][i] = min(st[k-1][i], st[k-1][i + (1 << (k-1))])

        answers = []
        for li, ri in queries:
            l = li - 1
            r = ri
            length = r - l + 1
            k = log_table[length]
            mid = r - (1 << k) + 1

            min_val = min(st[k][l], st[k][mid])
            ans = (ri - li + 1) - (a[l] - min_val) - (a[r] - min_val)
            answers.append(max(ans // 1, 0))  # 确保结果为整数

        return answers
