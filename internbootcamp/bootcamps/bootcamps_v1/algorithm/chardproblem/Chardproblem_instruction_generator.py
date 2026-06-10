import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re




class ChardproblemInstructionGenerator(BaseInstructionGenerator):
    """Chardproblem Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_string_length=10, min_n=2, **kwargs):
        """
        初始化Chardproblem指令生成器
        
        Args:
            max_n: 参数描述
            max_string_length: 参数描述
            min_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.min_n = min_n
        self.max_n = max_n
        self.max_string_length = max_string_length
    
    def case_generator(self):
        """生成包含边界情况的测试案例"""
        n = random.randint(self.min_n, self.max_n)
        c = [random.randint(0, 10) for _ in range(n)]
        strings = self._generate_strings_with_edge_cases(n)
        
        case = {
            'n': n,
            'c': c,
            'strings': strings,
            'expected_output': self._solve_case(n, c, strings)
        }
        return case
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_example = f"{question_case['n']}\n"
        input_example += ' '.join(map(str, question_case['c'])) + '\n'
        input_example += '\n'.join(question_case['strings'])
        return f"""请解决下列字符串排序能量消耗问题：
{input_example}
答案格式：[answer]答案[/answer]，如[answer]-1[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_strings_with_edge_cases(self, n):
        """生成包含前缀、相同字符串等边界情况的序列"""
        strings = []
        if random.random() < 0.3:
            base = self._random_string()
            strings.append(base)
            for _ in range(n-1):
                strings.append(base + self._random_string(1))
        elif random.random() < 0.3: 
            s = self._random_string()
            strings = [s] * n
        else:
            total_length = 0
            for _ in range(n):
                max_len = min(self.max_string_length, 100000 - total_length)
                if max_len <=0:
                    s = ''
                else:
                    length = random.randint(1, max_len)
                    s = ''.join(random.choices(string.ascii_lowercase, k=length))
                    total_length += length
                strings.append(s)
        return strings

    def _random_string(self, length=None):
        """生成随机长度的字符串"""
        if length is None:
            length = random.randint(1, self.max_string_length)
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _solve_case(self, n, c, strings):
        """动态规划求解正确结果 (完整实现)"""
        dp = [[-1] * 2 for _ in range(n)]
        dp[0][0] = 0
        dp[0][1] = c[0]
        possible = True

        for i in range(1, n):
            prev = strings[i-1]
            current = strings[i]
            prev_rev = prev[::-1]
            current_rev = current[::-1]

            dp_i0 = -1
            dp_i1 = -1

            # 处理不反转当前字符串的情况
            if dp[i-1][0] != -1 and current >= prev:
                dp_i0 = dp[i-1][0]
            if dp[i-1][1] != -1 and current >= prev_rev:
                if dp_i0 == -1 or dp[i-1][1] < dp_i0:
                    dp_i0 = dp[i-1][1]

            # 处理反转当前字符串的情况
            cost = c[i]
            if dp[i-1][0] != -1 and current_rev >= prev:
                dp_i1 = dp[i-1][0] + cost
            if dp[i-1][1] != -1 and current_rev >= prev_rev:
                candidate = dp[i-1][1] + cost
                if dp_i1 == -1 or candidate < dp_i1:
                    dp_i1 = candidate

            dp[i][0] = dp_i0
            dp[i][1] = dp_i1

            if dp[i][0] == -1 and dp[i][1] == -1:
                possible = False
                break

        if not possible:
            return -1

        final0 = dp[-1][0]
        final1 = dp[-1][1]
        if final0 == -1 and final1 == -1:
            return -1
        return min(filter(lambda x: x != -1, [final0, final1])) if final0 != -1 and final1 != -1 else max(final0, final1)
