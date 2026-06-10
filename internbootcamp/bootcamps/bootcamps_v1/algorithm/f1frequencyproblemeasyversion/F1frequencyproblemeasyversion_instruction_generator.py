import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import defaultdict
import random
import re




class F1frequencyproblemeasyversionInstructionGenerator(BaseInstructionGenerator):
    """F1frequencyproblemeasyversion Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=2000, max_val=100):
        """
        初始化F1frequencyproblemeasyversion指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """将默认n_max从200000调整为2000以保证生成效率"""
        self.n_min = n_min
        self.n_max = n_max
        self.max_val = max_val
    
    def case_generator(self):
        case_type = random.choice(['random', 'multi_max', 'single_max', 'edge'])
        max_case_size = 2000  # 所有案例统一限制最大尺寸

        if case_type == 'multi_max':
            # 生成两个最高频元素
            n = random.randint(2, min(max_case_size, self.n_max))
            val1, val2 = random.sample(range(1, self.max_val+1), 2)
            return self._create_multi_max_case(n, val1, val2)
        
        elif case_type == 'single_max':
            # 生成带有有效子数组的结构
            n = random.randint(3, min(max_case_size, self.n_max))
            return self._create_single_max_case(n)
        
        elif case_type == 'edge':
            # 边界情况处理
            return {'array': [random.randint(1, self.max_val)], 'answer': 0}
        
        else:  # random case
            n = random.randint(self.n_min, min(max_case_size, self.n_max))
            arr = [random.randint(1, self.max_val) for _ in range(n)]
            return {
                'array': arr,
                'answer': self._optimized_solve(arr)
            }
    
    @staticmethod
    def prompt_func(question_case):
        # 保持原有prompt生成逻辑不变
        array = question_case['array']
        return f"""题目要求：找出最长子数组使得出现次数最多的值的频次不唯一。
输入数组长度：{len(array)}
数组元素：{' '.join(map(str, array))}
请将答案放在[answer]标签内。示例：[answer]5[/answer]

你的解答：""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _create_multi_max_case(self, n, val1, val2):
        """创建两个最高频次相同的案例"""
        k = random.randint(1, n//2)
        arr = [val1]*k + [val2]*k
        if n > 2*k:
            arr += random.choices([val1, val2], k=n-2*k)
        random.shuffle(arr)
        return {'array': arr, 'answer': n}

    def _create_single_max_case(self, n):
        """创建存在有效子数组的案例"""
        main_val = random.randint(1, self.max_val)
        sec_val = random.choice([x for x in range(1, self.max_val+1) if x != main_val])

        # 确保存在有效子数组
        arr = [main_val]*(n-2) + [sec_val]*2
        random.shuffle(arr)
        return {'array': arr, 'answer': self._optimized_solve(arr)}

    def _optimized_solve(self, array):
        """优化后的求解算法"""
        freq = defaultdict(int)
        for num in array:
            freq[num] += 1

        # 找出前两个最高频元素
        sorted_freq = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
        if len(sorted_freq) >= 2 and sorted_freq[0][1] == sorted_freq[1][1]:
            return len(array)

        if not sorted_freq:
            return 0

        # 仅考虑前两个可能候选元素
        main_val = sorted_freq[0][0]
        candidates = [item[0] for item in sorted_freq[1:min(5, len(sorted_freq))]]
        max_len = 0

        for candidate in candidates:
            current_len = self._find_length(array, main_val, candidate)
            max_len = max(max_len, current_len)

        return max_len if max_len > 0 else 0

    def _find_length(self, arr, val1, val2):
        """优化后的子数组查找算法"""
        prefix_sum = 0
        first_occurrence = {0: -1}
        max_len = 0

        for idx, num in enumerate(arr):
            if num == val1:
                prefix_sum += 1
            elif num == val2:
                prefix_sum -= 1

            if prefix_sum in first_occurrence:
                max_len = max(max_len, idx - first_occurrence[prefix_sum])
            else:
                first_occurrence[prefix_sum] = idx

        return max_len
