import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import defaultdict
import random
import re




class D1frequencyproblemeasyversionInstructionGenerator(BaseInstructionGenerator):
    """D1frequencyproblemeasyversion Bootcamp指令生成器"""
    
    def __init__(self, max_n=100):
        """
        初始化D1frequencyproblemeasyversion指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n  # 控制生成数组的最大长度
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        max_val = min(n, 100)
        a = [random.randint(1, max_val) for _ in range(n)]
        ans = self.calculate_answer(a)
        return {
            'n': n,
            'array': a,
            'answer': ans
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        array = ' '.join(map(str, question_case['array']))
        return f"""你是编程竞赛选手，请解决以下问题。给定一个数组，找出最长的子数组，使得该子数组中出现次数最多的元素不是唯一的。输出该子数组长度。

输入格式：
第一行：n (数组长度)
第二行：数组元素，空格分隔

示例输入：
7
1 1 2 2 3 3 3

示例输出：
6

当前问题：
n = {n}
数组为：{array}

请将最终答案放置在[answer]标签内，如：[answer]6[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_answer(a):
        """完全对齐参考代码的实现逻辑"""
        freq = defaultdict(int)
        for num in a:
            freq[num] += 1
        if not freq:
            return 0

        # 确定最大频率元素
        mx = max(freq.values())
        cnt = sum(1 for v in freq.values() if v == mx)
        ele = next(k for k, v in freq.items() if v == mx)

        # Case 1: 多个元素达到最大频率
        if cnt >= 2:
            return len(a)

        # Case 2: 单个最大频率元素时
        max_length = 0
        for candidate in range(1, 101):
            if candidate == ele:
                continue

            # 使用前缀和算法查找最长子数组
            prefix_sum = {0: -1}
            current_sum = 0
            for idx, num in enumerate(a):
                if num == ele:
                    current_sum += 1
                elif num == candidate:
                    current_sum -= 1

                if current_sum in prefix_sum:
                    max_length = max(max_length, idx - prefix_sum[current_sum])
                else:
                    prefix_sum[current_sum] = idx

        return max_length
