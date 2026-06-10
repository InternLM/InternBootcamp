import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class ComkarandbaseballInstructionGenerator(BaseInstructionGenerator):
    """Comkarandbaseball Bootcamp指令生成器"""
    
    def __init__(self, min_n=5, max_n=10, answer_type=None):
        """
        初始化Comkarandbaseball指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            answer_type: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = max(1, min_n)
        self.max_n = max(self.min_n, max_n)
        self.answer_type = answer_type  # 先初始化属性
        if self.answer_type is not None and self.answer_type not in [0, 1, 2]:
            raise ValueError("answer_type must be 0, 1, 2, or None")
    
    def case_generator(self):
        # 确保answer_type有效性
        answer_type = self.answer_type if self.answer_type is not None else random.choice([0, 1, 2])
        
        # 处理最小尺寸约束
        min_n = self.min_n
        max_n = self.max_n
        if answer_type in {1, 2}:
            min_n = max(2, min_n)
            max_n = max(min_n, max_n)
        
        # 生成合法n值
        n = random.randint(min_n, max_n) if min_n <= max_n else min_n

        # 三种答案类型生成策略
        if answer_type == 0:
            arr = list(range(1, n+1))
            answer = 0
        elif answer_type == 1:
            # 生成单次交换的排列
            while True:
                arr = list(range(1, n+1))
                # 随机选择可交换区间
                start = random.randint(0, n-2)
                end = random.randint(start+1, n-1)
                sub = arr[start:end+1]
                # 生成错位排列（循环右移）
                derangement = sub[1:] + sub[:1]
                arr[start:end+1] = derangement
                if self._compute_answer(arr) == 1:
                    answer = 1
                    break
        else:
            # 生成需要两次交换的排列
            while True:
                arr = list(range(1, n+1))
                # 生成第一个错位区间
                start1 = random.randint(0, n-3)
                end1 = random.randint(start1+1, n-2)
                sub1 = arr[start1:end1+1]
                arr[start1:end1+1] = sub1[1:] + sub1[:1]
                
                # 生成第二个错位区间
                start2 = random.randint(end1+1, n-1)
                end2 = random.randint(start2+1, n-1) if start2 < n-1 else start2
                sub2 = arr[start2:end2+1]
                if len(sub2) >= 2:
                    arr[start2:end2+1] = sub2[1:] + sub2[:1]
                
                if self._compute_answer(arr) == 2:
                    answer = 2
                    break

        return {
            'n': n,
            'arr': arr,
            'answer': answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        return f"""Patrick needs to sort his baseball score records using special exchanges. Given the permutation:
n = {question_case['n']}
{question_case['arr']}

Calculate the minimum number of special exchanges required. Put your final answer within [answer] and [/answer] tags. For example: [answer]2[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_answer(a):
        """根据官方参考代码实现的答案验证逻辑"""
        B = sorted(a)
        cnt = 0
        i, n = 0, len(a)
        while i < n:
            while i < n and a[i] == B[i]:
                i += 1
            flag = 0
            while i < n and a[i] != B[i]:
                i += 1
                flag = 1
            if flag:
                cnt += 1
        return cnt if cnt <= 1 else 2
