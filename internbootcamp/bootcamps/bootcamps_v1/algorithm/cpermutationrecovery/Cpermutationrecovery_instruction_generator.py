import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CpermutationrecoveryInstructionGenerator(BaseInstructionGenerator):
    """Cpermutationrecovery Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cpermutationrecovery指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = params.get('min_n', 3)
        self.max_n = params.get('max_n', 6)
        self.prob_negative = params.get('prob_negative', 0.3)
        self.prob_invalid = params.get('prob_invalid', 0.3)
    
    def case_generator(self):
        generate_invalid = random.random() < self.prob_invalid
        
        for _ in range(10):  # 多次尝试生成
            n = random.randint(self.min_n, self.max_n)
            p = list(range(1, n+1))
            random.shuffle(p)
            original_next = self.compute_next(p)
            case_next = [
                val if random.random() > self.prob_negative else -1
                for val in original_next
            ]
            
            if not generate_invalid:
                return {'n': n, 'next': case_next}
            else:
                modified_next = case_next.copy()
                valid_modifications = [i for i in range(n) if modified_next[i] != -1]
                random.shuffle(valid_modifications)
                
                for idx in valid_modifications[:5]:  # 最多尝试修改5个有效位置
                    i_1based = idx + 1
                    current_val = modified_next[idx]
                    
                    if random.random() < 0.5:
                        # 设置为比i小的值或无效大值
                        if current_val <= i_1based:
                            continue
                        new_val = random.randint(1, i_1based)
                    else:
                        new_val = random.randint(n+2, n+5)
                    
                    modified_next[idx] = new_val
                    if self._is_case_invalid(n, modified_next):
                        return {'n': n, 'next': modified_next}
                
                return {'n': n, 'next': case_next}
        
        return {'n': 3, 'next': [3,4,-1]}  # fallback
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        next_list = question_case['next']
        problem = f"""给定一个长度{n}的next数组，其中-1表示信息丢失。请恢复原始排列，使得非-1的next值满足：
- next_i是i之后第一个更大元素的最小下标(1-based)
- 若无则设为{n+1}

如果解不存在请输出-1。答案请放在[answer]标签内。

输入：
n={n}
next={next_list}

示例：当n=3且next=[2,3,4]时，排列应为[answer]1 2 3[/answer]"""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_next(p):
        n = len(p)
        next_list = [n + 1] * n
        stack = []
        for i in range(n):
            while stack and p[i] > p[stack[-1]]:
                j = stack.pop()
                next_list[j] = i + 1
            stack.append(i)
        return next_list

    @classmethod
    def _is_case_invalid(cls, n, next_list):
        long = []
        lens = 0
        fucked = False
        a = next_list.copy()
        for i in range(n):
            if a[i] == -1:
                a[i] = i+2 if lens == 0 else long[-1]
            current = a[i]

            if current != -1:
                if lens > 0 and current > long[-1]:
                    fucked = True
                elif lens == 0 or current < long[-1]:
                    long.append(current)
                    lens += 1

            if lens > 0 and i >= (long[-1]-1):
                long.pop()
                lens -= 1
        return fucked
