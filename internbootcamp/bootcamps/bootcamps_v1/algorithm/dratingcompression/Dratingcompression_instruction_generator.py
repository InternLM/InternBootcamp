import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque




class DratingcompressionInstructionGenerator(BaseInstructionGenerator):
    """Dratingcompression Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dratingcompression指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = params.get('max_n', 10)
        self.min_n = params.get('min_n', 1)
    
    def case_generator(self):
        """生成多样化测试案例，包含：完全随机、保证有效k=1、强制全无效等类型"""
        case_type = random.choice(['random', 'valid_k1', 'invalid_all'])
        n = random.randint(self.min_n, self.max_n)
        
        if case_type == 'valid_k1':
            # 生成保证k=1有效的案例（数组本身就是排列）
            a = list(range(1, n+1))
            random.shuffle(a)
        elif case_type == 'invalid_all':
            # 生成所有k都无效的案例（数组元素全相同）
            a = [1] * n
        else:
            # 完全随机生成
            a = [random.randint(1, n) for _ in range(n)]
        
        correct_answer = self.optimized_solve(n, a)
        return {
            'n': n,
            'a': a,
            'correct_answer': correct_answer,
            'case_type': case_type  # 用于验证时追踪
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a_str = ' '.join(map(str, question_case['a']))
        n = question_case['n']
        return f"""给定长度为{n}的数组：[{a_str}]
请对k=1到k={n}依次判断：
1. 计算k-compression数组（每个元素是连续k个元素的最小值）
2. 检查该数组是否是1到(n-k+1)的排列

输出：长度为{n}的二进制字符串，第k位为1表示有效。答案置于[answer][/answer]中。例如：[answer]1010[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def optimized_solve(self, n, a):
        """准确高效的解法实现"""
        answer = ['0'] * n

        # 预处理k=1的情况
        k1_valid = (sorted(a) == list(range(1, n+1)))
        answer[0] = '1' if k1_valid else '0'

        # 预处理每个位置的next smaller元素
        next_smaller = [n] * n
        prev_smaller = [-1] * n
        stack = []

        for i in range(n):
            while stack and a[i] < a[stack[-1]]:
                next_smaller[stack.pop()] = i
            prev_smaller[i] = stack[-1] if stack else -1
            stack.append(i)

        # 统计每个元素作为最小值的影响范围
        min_intervals = {}
        for i in range(n):
            left = prev_smaller[i] + 1
            right = next_smaller[i] - 1
            min_intervals[a[i]] = max(min_intervals.get(a[i], 0), right - left + 1)

        # 根据定理：当且仅当存在元素只能在窗口大小>=某个值时出现
        for m in range(1, n):
            max_k = n - m + 1
            if m in min_intervals and min_intervals[m] >= m:
                for k in range(max(1, m), max_k+1):
                    if k <= min_intervals[m]:
                        answer[k-1] = '1'

        # 最终验证每个k的结果
        for k in range(1, n+1):
            m = n - k + 1
            if m < 1:
                continue
            if answer[k-1] == '1':
                # 二次验证确保正确性
                window_min = self.sliding_window_min(a, k)
                if not self.is_permutation(window_min, m):
                    answer[k-1] = '0'
        return ''.join(answer)

    @staticmethod
    def sliding_window_min(arr, k):
        """精确计算滑动窗口的最小值"""
        dq = deque()
        result = []
        for i, num in enumerate(arr):
            while dq and arr[dq[-1]] >= num:
                dq.pop()
            dq.append(i)

            if dq[0] == i - k:
                dq.popleft()

            if i >= k - 1:
                result.append(arr[dq[0]])
        return result

    @staticmethod
    def is_permutation(nums, m):
        """验证是否为1~m的排列"""
        return len(nums) == m and set(nums) == set(range(1, m+1)) and len(set(nums)) == m
