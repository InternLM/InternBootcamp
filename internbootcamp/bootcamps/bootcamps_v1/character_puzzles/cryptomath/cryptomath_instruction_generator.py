import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import ast
import json
import sys
import random
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.cryptomath.lib.crypto_math import generate_crypto_math




class CryptomathInstructionGenerator(BaseInstructionGenerator):
    """Cryptomath Bootcamp指令生成器"""
    
    def __init__(self, num_letters=5, num_add=4, *args, **kwargs):
        """
        初始化Cryptomath指令生成器
        
        Args:
            num_letters: 参数描述
            num_add: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        # description = "略"
        # super().__init__(description,*args, **kwargs)
        self.num_letters = num_letters
        self.num_add = num_add
    
    def case_generator(self):
        puzzle = self.generator()
        self.prompt = self.get_question()
        self.prompt += self.get_question_following()

        return self.parse_question(self.prompt)
    
    def prompt_func(self, identity) -> str:
        return self.prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generator(self):
        results = generate_crypto_math(self.num_letters, 1, self.num_add)
        puzzle = results[0]["puzzle"]
        self.puzzle = puzzle
        return self.puzzle

    def get_question(self):
        statements = [f"""你是一个专门解决定制谜题问题的智能助手。请准确应用下面的规则解答题目。

谜题规则：
给出一个字母公式，每个字母代表一个唯一数字（0-9）。不同字母不能代表相同数字，任何多位数的首字母不能为 0。

问题：
{self.puzzle}

请以字母=数字的形式给出答案，并将最终答案用双括号括起来，例如：[[A=1,B=2,...]]。

答案："""]

        return random.choice(statements)


    def get_question_following(self):
        followings = []
        followings.append("""\n
    等于数字的形式给出你的答案，并且把答案放在双括号内，比如这样：[[A=1,B=2,...]]。""")
        return random.choice(followings)

    @staticmethod
    def parse_question(question: str) -> dict:
        pattern = r'(?:问题|题目|输入算式为|问题是)[：:]\s*([A-Z+]+=[A-Z]+)'
        match = re.search(pattern, question)
        if not match:
            return None
        equation = match.group(1)
        left, right = equation.split('=')
        terms = left.split('+')
        leading_letters = set()
        letters = set()
        for term in terms + [right]:
            letters.update(term)
            if len(term) > 1:
                leading_letters.add(term[0])
        return {
            'left_terms': terms,
            'right_term': right,
            'leading_letters': list(leading_letters),
            'all_letters': list(letters)
        }

    @staticmethod
    def check_solution(parsed_question: dict, parsed_response: dict) -> bool:
        def has_solution(pq):
            letters = list(pq['all_letters'])
            leading = pq['leading_letters']
            n = len(letters)
            for perm in permutations(range(10), n):
                assignment = dict(zip(letters, perm))
                valid = all(assignment[l] != 0 for l in leading)
                if not valid:
                    continue
                left_sum = 0
                for term in pq['left_terms']:
                    num = 0
                    for c in term:
                        num = num * 10 + assignment[c]
                    left_sum += num
                right_num = 0
                for c in pq['right_term']:
                    right_num = right_num * 10 + assignment[c]
                if left_sum == right_num:
                    return True
            return False

        if parsed_response is None:
            return not has_solution(parsed_question)
        else:
            pq = parsed_question
            resp = parsed_response
            leading = pq['leading_letters']
            for letter in leading:
                if resp.get(letter, 0) == 0:
                    return False
            values = list(resp.values())
            if len(values) != len(set(values)):
                return False
            if set(resp.keys()) != set(pq['all_letters']):
                return False
            left_sum = 0
            for term in pq['left_terms']:
                num = 0
                for c in term:
                    num = num * 10 + resp[c]
                left_sum += num
            right_num = 0
            for c in pq['right_term']:
                right_num = right_num * 10 + resp[c]
            return left_sum == right_num
