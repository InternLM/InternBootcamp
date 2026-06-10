import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from math import pow




class DhugestringsInstructionGenerator(BaseInstructionGenerator):
    """Dhugestrings Bootcamp指令生成器"""
    
    def __init__(self, n_max=5, m_max=3, max_total_length=100):
        """
        初始化Dhugestrings指令生成器
        
        Args:
            n_max: 参数描述
            m_max: 参数描述
            max_total_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_max = min(n_max, 100)
        self.m_max = min(m_max, 100)
        self.max_total_length = min(max_total_length, 100)
    
    def case_generator(self):
        # 生成初始字符串逻辑优化
        initial_strings = []
        total_length = 0
        target_count = random.randint(1, self.n_max)
        
        while len(initial_strings) < target_count and total_length < self.max_total_length:
            remaining = self.max_total_length - total_length
            length = random.randint(1, min(100, remaining))
            s = ''.join(random.choices(['0','1'], k=length))
            initial_strings.append(s)
            total_length += length

        # 生成操作序列逻辑完善
        m = random.randint(1, self.m_max)
        s_states = []
        for s in initial_strings:
            pre = s[:9]
            suf = s[-9:] if len(s)>=9 else s
            s_states.append((
                pre,
                suf,
                self.mset(s)
            ))
        
        operations = []
        answers = []
        for _ in range(m):
            current_count = len(s_states)
            ai = random.randint(1, current_count)
            bi = random.randint(1, current_count)
            operations.append((ai, bi))
            
            # 状态更新逻辑
            a_state = s_states[ai-1]
            b_state = s_states[bi-1]
            
            # 计算新前缀
            new_pre = a_state[0]
            if len(new_pre) < 9:
                new_pre = (new_pre + b_state[0])[:9]
            
            # 计算新后缀
            new_suf = b_state[1]
            if len(new_suf) < 9:
                combined = a_state[1] + b_state[1]
                new_suf = combined[-9:]
            
            # 计算中间组合
            mid_str = a_state[1] + b_state[0]
            mid_set = self.mset(mid_str)
            combined_set = a_state[2].union(b_state[2]).union(mid_set)
            
            # 关键修正：最大k值计算逻辑
            max_k = 0
            for k in range(1, 10):
                required = 2 ** k
                all_exist = True
                for num in range(required):
                    target = bin(num)[2:].zfill(k)
                    if target not in combined_set:
                        all_exist = False
                        break
                if all_exist:
                    max_k = k
            answers.append(max_k if max_k > 0 else 0)
            
            s_states.append((new_pre, new_suf, combined_set))
        
        return {
            'initial': initial_strings,
            'operations': operations,
            'answers': answers
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_str = f"{len(question_case['initial'])}\n"
        input_str += "\n".join(question_case['initial']) + "\n"
        input_str += f"{len(question_case['operations'])}\n"
        for a, b in question_case['operations']:
            input_str += f"{a} {b}\n"
        
        return f"""You are given {len(question_case['initial'])} binary strings and {len(question_case['operations'])} concatenation operations. After each operation, determine the maximum positive integer k such that all possible binary strings of length k are present as substrings in the new string. If no such k exists, output 0.

Input:
{input_str.strip()}

Output your answers for each operation in order, each on a new line enclosed within [answer] tags. Example:
[answer]
1
2
0
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def mset(s):
        substr_set = set()
        for k in range(10):
            for num in range(2**k):
                bin_str = bin(num)[2:].zfill(k)
                if bin_str in s:
                    substr_set.add(bin_str)
        return substr_set
