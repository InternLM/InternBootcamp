import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from itertools import permutations




class KorpuzzlecryptomathInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzlecryptomath Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Korpuzzlecryptomath指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数:
            min_terms: 加数最小数量 (默认2)
            max_terms: 加数最大数量 (默认3)
            term_length: 项的数字位数 (默认3)
            result_length: 结果的数字位数 (默认4)
        """
        self.min_terms = params.get('min_terms', 2)
        self.max_terms = params.get('max_terms', 3)
        self.term_length = params.get('term_length', 3)
        self.result_length = params.get('result_length', 4)
    
    def case_generator(self):
        """生成动态有效的字母算术方程"""
        equation = self._generate_valid_equation()
        return {"equation": equation}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        equation = question_case["equation"]
        prompt = f"""Solve this cryptarithmetic puzzle where each letter represents a unique digit (0-9). 
Different letters must have different values. Leading letters cannot be zero. 

Equation: {equation}

Provide your answer as comma-separated letter=number pairs enclosed in double square brackets. 
Example: [[A=5,B=3,...,Z=9]]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_equation(self):
        """动态生成有效等式"""
        # 生成随机加法结构：A + B + ... = SUM
        num_terms = random.randint(self.min_terms, self.max_terms)

        while True:
            # 生成随机数字组合
            digits = random.sample(range(0, 10), self.term_length)
            terms = [random.randint(10**(self.term_length-1), 10**self.term_length-1) 
                    for _ in range(num_terms)]
            total = sum(terms)

            if len(str(total)) == self.result_length:
                # 转换为字母模式
                letters = set()
                equation_parts = []
                for term in terms + [total]:
                    term_str = str(term)
                    if len(term_str) < self.term_length:
                        term_str = term_str.zfill(self.term_length)
                    equation_parts.append(term_str)
                    letters.update(term_str)

                # 确保结果首位非零
                if equation_parts[-1][0] == '0':
                    continue

                # 转换为字母方程
                char_map = {}
                unique_chars = list(letters)
                random.shuffle(unique_chars)
                for c in unique_chars:
                    char_map[c] = chr(65 + len(char_map))  # 映射到不同字母

                equation = []
                for part in equation_parts[:-1]:
                    equation.append(''.join([char_map[c] for c in part]))
                result = ''.join([char_map[c] for c in equation_parts[-1]])

                return f"{'+'.join(equation)}={result}"
