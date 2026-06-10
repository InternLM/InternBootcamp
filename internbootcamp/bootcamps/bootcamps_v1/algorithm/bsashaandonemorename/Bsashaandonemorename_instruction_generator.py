import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re




class BsashaandonemorenameInstructionGenerator(BaseInstructionGenerator):
    """Bsashaandonemorename Bootcamp指令生成器"""
    
    def __init__(self, case_type=None, min_length=3, max_length=20):
        """
        初始化Bsashaandonemorename指令生成器
        
        Args:
            case_type: 参数描述
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.case_type = case_type
        self.min_length = min_length
        self.max_length = max_length
    
    def case_generator(self):
        case_type = self.case_type if self.case_type in ['impossible', 'k1', 'k2'] else random.choice(['impossible', 'k1', 'k2'])
        
        while True:
            if case_type == 'impossible':
                s = self._generate_impossible_case()
                if len(set(s)) == 1:
                    return {'s': s}
            elif case_type == 'k1':
                s = self._generate_k1_case()
                if any(self._is_valid_rotation(s, i) for i in range(1, len(s))):
                    return {'s': s}
            else:
                s = self._generate_k2_case()
                if not any(self._is_valid_rotation(s, i) for i in range(1, len(s))):
                    return {'s': s}
    
    @staticmethod
    def prompt_func(question_case):
        s = question_case['s']
        return f"""根据神秘东方命名规则，你需要将一个回文字符串{s}分割重组为不同的回文：
1. 只能通过切割并重组子串来形成新回文
2. 新回文必须与原字符串不同
3. 需要找到最小切割次数k

请按照以下格式给出答案：[answer]答案[/answer]
示例：
输入：nolon → [answer]2[/answer]
输入：otto → [answer]1[/answer]
输入：qqqq → [answer]Impossible[/answer]
""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_impossible_case(self):
        n = random.randint(self.min_length, self.max_length)
        c = random.choice(string.ascii_lowercase)
        return c * n

    def _generate_k1_case(self):
        while True:
            base = ''.join(random.choices(string.ascii_lowercase, k=random.randint(2, self.max_length//2)))
            if base != base[::-1]:
                s = base + base[::-1]
                if s != s[::-1]:
                    continue
                return s

    def _generate_k2_case(self):
        while True:
            s = self._generate_complex_palindrome()
            if all(c == s[0] for c in s):
                continue
            return s

    def _generate_complex_palindrome(self):
        """生成无法通过简单旋转得到不同解的复杂回文"""
        while True:
            left = []
            for _ in range(random.randint(2, self.max_length//2)):
                candidates = [c for c in string.ascii_lowercase if not left or c != left[-1]]
                left.append(random.choice(candidates))
            left_str = ''.join(left)
            right_str = left_str[::-1]

            if random.choice([True, False]) and len(left_str) > 1:
                mid = random.choice(string.ascii_lowercase.replace(left_str[-1], ''))
            else:
                mid = ''
            s = left_str + mid + right_str

            if not any(self._is_valid_rotation(s, i) for i in range(1, len(s))):
                return s

    @staticmethod
    def _is_valid_rotation(s, i):
        rotated = s[i:] + s[:i]
        return rotated != s and rotated == rotated[::-1]
