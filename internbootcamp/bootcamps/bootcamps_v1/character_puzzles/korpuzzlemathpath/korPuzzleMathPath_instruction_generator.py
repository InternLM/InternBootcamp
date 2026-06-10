import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def evaluate_expression(numbers, operators):
    nums = numbers.copy()
    ops = operators.copy()
    
    # 处理乘除运算
    i = 0
    while i < len(ops):
        if ops[i] in ('*', '/'):
            a = nums[i]
            b = nums[i+1]
            try:
                if ops[i] == '*':
                    res = a * b
                else:
                    res = a // b if b != 0 else 0
                nums[i] = res
                del nums[i+1]
                del ops[i]
            except:
                return None
        else:
            i += 1
    
    # 处理加减运算
    try:
        result = nums[0]
        for i in range(len(ops)):
            if ops[i] == '+':
                result += nums[i+1]
            else:
                result -= nums[i+1]
        return result
    except:
        return None


class KorpuzzlemathpathInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzlemathpath Bootcamp指令生成器"""
    
    def __init__(self, max_ops=4, allow_division=True, min_target=-50, max_target=100):
        """
        初始化Korpuzzlemathpath指令生成器
        
        Args:
            max_ops: 参数描述
            allow_division: 参数描述
            min_target: 参数描述
            max_target: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'max_ops': max_ops,
            'allow_division': allow_division,
            'min_target': min_target,
            'max_target': max_target,
            'max_attempts': 100
        }
    
    def case_generator(self):
        allowed_ops = ['+', '-', '*']
        if self.params['allow_division']:
            allowed_ops.append('/')
        
        for _ in range(self.params['max_attempts']):
            n_ops = random.randint(1, self.params['max_ops'])
            ops = [random.choice(allowed_ops) for _ in range(n_ops)]
            num_vars = n_ops + 1
            numbers = []
            valid = True
            
            numbers.append(random.randint(0, 9))
            for i in range(n_ops):
                op = ops[i]
                if op == '/':
                    prev_num = numbers[i]
                    if prev_num == 0:
                        next_num = random.randint(1, 9)
                    else:
                        possible_divisors = [x for x in range(1, 10) if x != 0 and prev_num % x == 0]
                        if not possible_divisors:
                            valid = False
                            break
                        next_num = random.choice(possible_divisors)
                    numbers.append(next_num)
                else:
                    numbers.append(random.randint(0, 9))
            
            if not valid:
                continue
            
            target = evaluate_expression(numbers, ops)
            if target is None:
                continue
            if not (self.params['min_target'] <= target <= self.params['max_target']):
                continue
            
            return {
                'operators': ops,
                'target': target,
                'num_vars': num_vars
            }
        
        return {
            'operators': ['+', '*'],
            'target': 10,
            'num_vars': 3
        }
    
    @staticmethod
    def prompt_func(question_case):  # 修正此处缩进
        operators = question_case['operators']
        target = question_case['target']
        equation = '?'
        for op in operators:
            equation += f'{op}?'
        equation += f'={target}'
        
        prompt = f"""你是一位数学谜题解答专家，需要解决以下等式问题。请用0到9的数字填入问号，使等式成立。遵循数学中的运算顺序规则（先乘除，后加减）。

等式： {equation}

要求：
- 每个问号必须填入一个0到9之间的整数
- 允许重复使用数字
- 严格按照正确运算顺序计算结果

请提供一个可行的解，并将完整等式用双括号括起来，例如：[[答案填入这里]]。确保将最终答案放置在双括号内。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

