import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import bisect
from collections import defaultdict
import random




class CmollyschemicalsInstructionGenerator(BaseInstructionGenerator):
    """Cmollyschemicals Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10, min_abs_k=1, max_abs_k=10, array_min=-100, array_max=100):
        """
        初始化Cmollyschemicals指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_abs_k: 参数描述
            max_abs_k: 参数描述
            array_min: 参数描述
            array_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_abs_k = max(1, min_abs_k)  # 确保最小绝对值为1
        self.max_abs_k = max_abs_k
        self.array_min = array_min
        self.array_max = array_max
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        # 强制k_abs的取值范围在有效区间
        k_abs = random.randint(self.min_abs_k, self.max_abs_k)
        k = k_abs if random.random() < 0.5 else -k_abs
        array = [random.randint(self.array_min, self.array_max) for _ in range(n)]
        correct_answer = self._calculate_solution(n, k, array)
        return {
            'n': n,
            'k': k,
            'array': array,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        k = question_case['k']
        array = question_case['array']
        array_str = ' '.join(map(str, array))
        prompt = f"""Molly Hooper has {n} chemicals arranged in a line. Each chemical has an affection value. Find the number of contiguous segments where the total affection value is a non-negative integer power of {k}.

Input:
{n} {k}
{array_str}

Your answer must be a single integer placed between [answer] and [/answer] tags. Example: [answer]8[/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _calculate_solution(n, k, array):
        pre = []
        current_sum = 0
        for num in array:
            current_sum += num
            pre.append(current_sum)
        ocr = defaultdict(list)
        for idx, s in enumerate(pre):
            ocr[s].append(idx)
        ans = 0
        INF = 10**14 + 10

        for i in range(n):
            at_ = pre[i]
            for j in range(0, 51):
                to_ = k ** j
                if k not in (1, -1) and abs(to_) > INF:
                    break
                # 处理单元素段
                if array[i] == to_:
                    ans += 1
                # 处理完整前缀段
                if i != 0 and at_ == to_:
                    ans += 1
                check_ = at_ - to_
                if check_ in ocr:
                    arr = ocr[check_]
                    ax = bisect.bisect_left(arr, i)
                    if ax > 0:
                        atx = arr[ax-1]
                        if (i - atx) > 1:
                            ans += ax
                        else:
                            ans += max(0, ax-1)
                # 处理k的特殊情况
                if k == 1:
                    break
                if k == -1 and j == 1:
                    break
        return ans
