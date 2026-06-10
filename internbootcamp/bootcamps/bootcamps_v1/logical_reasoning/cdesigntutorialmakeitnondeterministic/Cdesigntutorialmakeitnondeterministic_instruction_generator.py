import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def solve_handle_order(names, p_list):
    if not names or len(p_list) != len(names):
        return "NO"
    n = len(names)
    p = p_list
    Flag = True
    current_user = names[p[0]-1]
    a, b = current_user
    Tmp = a if a < b else b
    for i in range(1, len(p)):
        current_user = names[p[i]-1]
        a, b = current_user
        current_min = a if a < b else b
        current_max = b if a < b else a
        if Tmp >= current_min:
            if Tmp >= current_max:
                Flag = False
                break
            else:
                Tmp = current_max
        else:
            Tmp = current_min
    return "YES" if Flag else "NO"

def generate_random_string(min_length=1, max_length=50):
    length = random.randint(min_length, max_length)
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length))


class CdesigntutorialmakeitnondeterministicInstructionGenerator(BaseInstructionGenerator):
    """Cdesigntutorialmakeitnondeterministic Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=10, solvable=None, max_attempts=1000):
        """
        初始化Cdesigntutorialmakeitnondeterministic指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            solvable: 参数描述
            max_attempts: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()  # 显式调用父类初始化
        self.min_n = min_n
        self.max_n = max_n
        self.solvable = solvable
        self.max_attempts = max_attempts
    
    def case_generator(self):
        for _ in range(self.max_attempts):
            # 保证n至少为1
            n = random.randint(max(1, self.min_n), self.max_n)
            
            names = []
            all_names = set()
            valid = True
            
            # 为每个用户生成唯一的名字对
            for _ in range(n):
                attempt = 0
                while True:
                    first = generate_random_string(1, 50)
                    last = generate_random_string(1, 50)
                    if first != last and first not in all_names and last not in all_names:
                        all_names.update([first, last])
                        names.append((first, last))
                        break
                    attempt += 1
                    if attempt > 100:
                        valid = False
                        break
                if not valid:
                    break
            if not valid:
                continue
            
            # 生成有效排列p
            p = list(range(1, n+1))
            random.shuffle(p)
            answer = solve_handle_order(names, p)
            
            # 根据solvable参数筛选案例
            if self.solvable is None:
                return {'n': n, 'names': names, 'p': p}
            elif (self.solvable and answer == "YES") or (not self.solvable and answer == "NO"):
                return {'n': n, 'names': names, 'p': p}
        
        # 备用方案：生成确定性的可解/不可解案例
        if self.solvable:
            return {'n': 3, 'names': [('a','z'), ('b','y'), ('c','x')], 'p': [3,2,1]}
        else:
            return {'n': 3, 'names': [('z','a'), ('y','b'), ('x','c')], 'p': [1,2,3]}
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [str(question_case['n'])]
        for first, last in question_case['names']:
            input_lines.append(f"{first} {last}")
        input_lines.append(' '.join(map(str, question_case['p'])))
        example_input = '\n'.join(input_lines)
        
        prompt = (
            "给定n个人，每个人可以选择使用名字或姓氏作为handle。\n"
            "判断是否存在一种选择方式，使得按handle的字典序结果恰好等于给定的排列p。\n\n"
            "输入格式：\n"
            f"- 首行：n（人数）\n"
            f"- 接下来n行：每行两个小写字母组成的字符串\n"
            f"- 最后一行：排列p（1-based索引）\n\n"
            "示例：\n"
            "输入：\n3\na b\nc d\ne f\n3 1 2\n输出：YES\n\n"
            "当前问题输入：\n"
            f"{example_input}\n\n"
            "请将最终答案放在[answer]和[/answer]标签之间。"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

