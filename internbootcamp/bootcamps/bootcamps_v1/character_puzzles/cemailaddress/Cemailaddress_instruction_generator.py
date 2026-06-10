import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re




class CemailaddressInstructionGenerator(BaseInstructionGenerator):
    """Cemailaddress Bootcamp指令生成器"""
    
    def __init__(self, min_local_length=3, max_local_length=10, min_domain_length=3, max_domain_length=10):
        """
        初始化Cemailaddress指令生成器
        
        Args:
            min_local_length: 参数描述
            max_local_length: 参数描述
            min_domain_length: 参数描述
            max_domain_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_local_length = min_local_length
        self.max_local_length = max_local_length
        self.min_domain_length = min_domain_length
        self.max_domain_length = max_domain_length
    
    def case_generator(self):
        email, input_str = self._generate_email()
        return {
            'input': input_str,
            'answer': email
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_str = question_case['input']
        return f"""Convert the phone-spelled email address to proper format. Rules:
1. Replace 'at' with @ and 'dot' with . where possible
2. Result must be valid (exactly one @, no invalid start/end)
3. Choose the SHORTEST possible result
4. If same length, choose lexicographically smallest

Input: {input_str}
Put your final answer within [answer][/answer] tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_part(self, part_type):
        """生成符合规范的邮箱部分（local或domain）"""
        while True:
            length = random.randint(self.min_local_length if part_type == "local" else self.min_domain_length,
                                   self.max_local_length if part_type == "local" else self.max_domain_length)

            # 首尾必须是小写字母
            first = random.choice(string.ascii_lowercase)
            last = random.choice(string.ascii_lowercase)

            # 中间字符生成（避免连续点）
            middle = []
            for _ in range(length-2):
                choices = string.ascii_lowercase
                if middle and middle[-1] != '.':
                    choices += '.'
                middle.append(random.choice(choices))

            # 拼接并验证
            candidate = first + ''.join(middle) + last
            if '.' in candidate:
                candidate = re.sub(r'\.{2,}', '.', candidate)  # 移除连续点
            if (candidate[0] not in ('.', '@') and 
                candidate[-1] not in ('.', '@') and 
                '@' not in candidate):
                return candidate

    def _generate_email(self):
        """生成合法邮箱并确保对应输入字符串具有唯一最优解"""
        while True:
            local = self._generate_part("local")
            domain = self._generate_part("domain")
            email = f"{local}@{domain}"

            # 生成输入字符串并验证唯一最优解
            input_str = (
                email[0] +
                email[1:-1].replace('@', 'at').replace('.', 'dot') +
                email[-1]
            )

            # 确保输入字符串中仅包含一个at（对应邮箱中的@）
            if input_str.count('at') == 1 and 'at' not in [input_str[:2], input_str[-2:]]:
                return email, input_str
