import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_prefixes(s):
    sca = [0] * (len(s) + 1)
    scb = [0] * (len(s) + 1)
    for i in range(1, len(s) + 1):
        char = s[i-1]
        if char == 'A':
            sca[i] = sca[i-1] + 1
            scb[i] = scb[i-1]
        else:
            sca[i] = sca[i-1]
            scb[i] = scb[i-1] + 1
    return sca, scb

def compute_query_result(sca, scb, tca, tcb, a, b, c, d):
    sb = scb[b] - scb[a-1]
    sa = min(sca[b], b - a + 1)
    tb = tcb[d] - tcb[c-1]
    ta = min(tca[d], d - c + 1)

    if (sb ^ tb) & 1:
        return '0'
    if sa < ta:
        return '0'
    if (sa - ta) % 3 == 0:
        if sb > tb:
            return '0'
    else:
        if (sb + 2) > tb:
            return '0'
    if sb == 0 and tb != 0 and sa == ta:
        return '0'
    return '1'


class DpickingstringsInstructionGenerator(BaseInstructionGenerator):
    """Dpickingstrings Bootcamp指令生成器"""
    
    def __init__(self, max_s_length=10, max_t_length=10, max_queries=5, max_attempts=10):
        """
        初始化Dpickingstrings指令生成器
        
        Args:
            max_s_length: 参数描述
            max_t_length: 参数描述
            max_queries: 参数描述
            max_attempts: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_s_length = max_s_length
        self.max_t_length = max_t_length
        self.max_queries = max_queries
        self.max_attempts = max_attempts
    
    def case_generator(self):
        for _ in range(self.max_attempts):
            s = ''.join(random.choices(['A', 'B', 'C'], k=random.randint(1, self.max_s_length)))
            t = ''.join(random.choices(['A', 'B', 'C'], k=random.randint(1, self.max_t_length)))
            sca, scb = compute_prefixes(s)
            tca, tcb = compute_prefixes(t)
            a, b = 1, len(s)
            c, d = 1, len(t)
            if compute_query_result(sca, scb, tca, tcb, a, b, c, d) == '1':
                queries = [[a, b, c, d]]
                for _ in range(self.max_queries - 1):
                    a_q = random.randint(1, len(s))
                    b_q = random.randint(a_q, len(s))
                    c_q = random.randint(1, len(t))
                    d_q = random.randint(c_q, len(t))
                    queries.append([a_q, b_q, c_q, d_q])
                return {
                    'S': s,
                    'T': t,
                    'queries': queries
                }
        # Fallback if no valid case found
        s = ''.join(random.choices(['A', 'B', 'C'], k=random.randint(1, self.max_s_length)))
        t = ''.join(random.choices(['A', 'B', 'C'], k=random.randint(1, self.max_t_length)))
        queries = []
        for _ in range(self.max_queries):
            a = random.randint(1, len(s))
            b = random.randint(a, len(s))
            c = random.randint(1, len(t))
            d = random.randint(c, len(t))
            queries.append([a, b, c, d])
        return {
            'S': s,
            'T': t,
            'queries': queries
        }
    
    @staticmethod
    def prompt_func(question_case):
        s = question_case['S']
        t = question_case['T']
        queries = question_case['queries']
        prompt = f"""Alice有一个字符串S，内容为：{s}。Bob可以对该字符串的任意子串应用以下转换规则（次数不限、顺序不限）：

- 将单个'A'替换为'BC'；
- 将单个'B'替换为'AC'；
- 将单个'C'替换为'AB'；
- 将连续的三个'A'（即"AAA"）替换为空字符串（即删除）。

现有目标字符串T，内容为：{t}。你需要处理{len(queries)}个查询，每个查询询问是否存在一种可能，通过应用上述规则，将S的某个子串转换为T的对应子串。

每个查询的参数为四个整数a、b、c、d，表示：源子串是S的第a到第b个字符（包含两端，按1-based索引），目标子串是T的第c到第d个字符。要求判断是否可以进行这样的转换。

请依次对每个查询给出“是”（用'1'表示）或“否”（用'0'表示）的答案，并将所有答案按顺序组成一个连续的字符串，无需分隔符。

请将最终答案放置在[answer]和[/answer]标签之间。例如：[answer]101[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

