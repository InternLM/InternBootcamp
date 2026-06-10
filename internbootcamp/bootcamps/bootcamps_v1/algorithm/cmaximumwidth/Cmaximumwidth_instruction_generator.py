import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CmaximumwidthInstructionGenerator(BaseInstructionGenerator):
    """Cmaximumwidth Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=20, min_m=2, max_m=15):
        """
        初始化Cmaximumwidth指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'min_n': min_n,
            'max_n': max_n,
            'min_m': min_m,
            'max_m': max_m,
        }
    
    def case_generator(self):
        max_retry = 5
        for _ in range(max_retry):
            try:
                m = random.randint(
                    max(self.params['min_m'], 2),
                    min(self.params['max_m'], self.params['max_n'])
                )
                n = random.randint(
                    max(m, self.params['min_n']),
                    self.params['max_n']
                )

                # 生成策略优化
                gen_strategy = random.choices(
                    ['direct_insert', 'reverse_insert', 'balanced'],
                    weights=[0.3, 0.3, 0.4],
                    k=1
                )[0]

                t = []
                s = []
                
                # 生成逻辑优化
                if gen_strategy == 'direct_insert':
                    t = [chr(97 + random.randint(0, 25)) for _ in range(m)]
                    ptr = 0
                    for i in range(m):
                        gap = random.randint(0, n - m - ptr) if i < m-1 else 0
                        s += [chr(97 + random.randint(0, 25)) for _ in range(gap)]
                        s.append(t[i])
                        ptr += gap + 1
                    s += [chr(97 + random.randint(0, 25)) for _ in range(n - len(s))]
                
                elif gen_strategy == 'reverse_insert':
                    t = [chr(97 + random.randint(0, 25)) for _ in range(m)]
                    remaining_space = n - m
                    gaps = [random.randint(0, remaining_space) for _ in range(m-1)]
                    total_gaps = sum(gaps)
                    
                    if total_gaps > remaining_space:
                        scale = remaining_space / total_gaps
                        gaps = [int(g*scale) for g in gaps]
                    
                    for i in range(m):
                        s.append(t[i])
                        if i < m-1:
                            s += [chr(97 + random.randint(0,25)) for _ in range(gaps[i])]
                    s += [chr(97 + random.randint(0,25)) for _ in range(n - len(s))]
                
                else:  # balanced strategy
                    t = [chr(97 + random.randint(0, 25)) for _ in range(m)]
                    pos = sorted(random.sample(range(n), m))
                    s = [chr(97 + random.randint(0,25)) for _ in range(n)]
                    for i,p in enumerate(pos):
                        s[p] = t[i]

                s = ''.join(s[:n])  # 长度强制对齐
                t = ''.join(t)
                
                # 验证子序列
                def is_subsequence(s, t):
                    it = iter(s)
                    return all(c in it for c in t)
                
                if not is_subsequence(s, t):
                    continue  # 重试

                # 计算正确答案
                ans1 = []
                ptr = 0
                for c in t:
                    while ptr < len(s) and s[ptr] != c:
                        ptr += 1
                    ans1.append(ptr)
                    ptr += 1
                
                ans2 = []
                ptr = len(s) - 1
                for c in reversed(t):
                    while ptr >= 0 and s[ptr] != c:
                        ptr -= 1
                    ans2.append(ptr)
                    ptr -= 1
                ans2.reverse()
                
                max_width = max(ans2[i+1] - ans1[i] for i in range(m-1))

                return {
                    'n': n,
                    'm': m,
                    's': s,
                    't': t,
                    'correct_answer': max_width
                }

            except Exception as e:
                continue
        raise RuntimeError("生成有效案例失败")
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""请解决以下字符串序列问题：

输入格式：
第一行：n m（2 ≤ m ≤ n）
第二行：s（长度n）
第三行：t（长度m）

问题描述：
寻找s中满足s[p_i] = t[i]的严格递增下标序列p_1 < p_2 < ... < p_m。
定义序列宽度为相邻下标差的最大值，即max(p_{{i+1}} - p_i)。
求所有可能序列中的最大宽度。

输入数据：
{question_case['n']} {question_case['m']}
{question_case['s']}
{question_case['t']}

将答案用[answer]标签包裹，例如：[answer]3[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

