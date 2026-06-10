import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CarithmeticprogressionInstructionGenerator(BaseInstructionGenerator):
    """Carithmeticprogression Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=5, min_number=1, max_number=100):
        """
        初始化Carithmeticprogression指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_number: 参数描述
            max_number: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_number = min_number
        self.max_number = max_number
    
    def case_generator(self):
        case_type = random.choices([1,2,3,4,5], weights=[0.1,0.2,0.3,0.3,0.1])[0]
        
        if case_type == 1:  # n=1 的测试用例
            n = 1
            numbers = [random.randint(self.min_number, self.max_number)]
        elif case_type == 2:  # n=2 且差为偶数的测试用例
            n = 2
            a = random.randint(self.min_number, self.max_number)
            d = random.choice([2,4,6,8,10])
            numbers = [a, a+d]
        elif case_type == 3:  # 需要插入元素的测试用例
            m = random.randint(3, 5)
            n = m-1
            a = random.randint(self.min_number, self.max_number)
            d = random.randint(1, 5)
            arr = [a + i*d for i in range(m)]
            del_index = random.randint(1, m-2)
            del arr[del_index]
            numbers = arr
        elif case_type == 4:  # 无解的测试用例
            n = 3
            while True:
                a = random.randint(self.min_number, self.max_number)
                d1 = random.randint(1, 5)
                d2 = random.randint(1, 5)
                if d1 != d2:
                    numbers = sorted([a, a+d1, a+d1+d2+1])
                    break
        else:  # 随机测试用例
            n = random.randint(self.min_n, self.max_n)
            numbers = [random.randint(self.min_number, self.max_number) for _ in range(n)]
        
        numbers = random.sample(numbers, len(numbers))  # 打乱顺序
        solutions = self._solve_problem(n, numbers)
        return {
            'n': n,
            'numbers': numbers,
            'solutions': solutions
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        numbers_str = ' '.join(map(str, question_case['numbers']))
        return (
            f"Given {question_case['n']} numbers: {numbers_str}\n"
            "Find all possible numbers to add to form an arithmetic sequence.\n"
            "Output format:\n"
            "- If infinite solutions: [answer]-1[/answer]\n"
            "- If no solution: [answer]0[/answer]\n"
            "- Else: [answer]sorted_numbers[/answer]\n"
            "Example 1: [answer]-2 10[/answer]\n"
            "Example 2: [answer]-1[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _solve_problem(n, numbers):
        if n == 1:
            return -1

        arr = sorted(numbers)
        mindiff = min(arr[i+1]-arr[i] for i in range(len(arr)-1))

        cnt = 0
        need_insert = None
        for i in range(len(arr)-1):
            diff = arr[i+1] - arr[i]
            if diff != mindiff:
                cnt += 1
                if diff == 2*mindiff:
                    need_insert = arr[i] + mindiff
                else:
                    return 0  # 存在无法修正的差值

        if cnt == 0:
            ans = {arr[0]-mindiff, arr[-1]+mindiff}
            if n == 2 and (arr[1]-arr[0])%2 == 0:
                ans.add(arr[0] + (arr[1]-arr[0])//2)
            return sorted(ans)
        elif cnt == 1 and need_insert is not None:
            return [need_insert]
        else:
            return 0
