import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re




class CtryandcatchInstructionGenerator(BaseInstructionGenerator):
    """Ctryandcatch Bootcamp指令生成器"""
    
    def __init__(self, max_depth=3, case_type=None):
        """
        初始化Ctryandcatch指令生成器
        
        Args:
            max_depth: 参数描述
            case_type: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_depth = max_depth
        self.case_type = case_type  # 0: valid, 1: multiple valid, 2: unhandled
    
    def case_generator(self):
        case_type = self.case_type
        if case_type is None:
            case_type = random.choice([0, 1, 2])
        
        ex_type = self._random_string(5)
        correct_msg = self._random_string(10)
        other_ex = self._random_string(5)
        while other_ex == ex_type:
            other_ex = self._random_string(5)
        
        lines = []
        if case_type == 0:
            lines = [
                'try',
                f'throw({ex_type})',
                f'catch({ex_type}, "{correct_msg}")'
            ]
        elif case_type == 1:
            lines = [
                'try',
                'try',
                f'throw({ex_type})',
                f'catch({ex_type}, "{correct_msg}")',
                f'catch({other_ex}, "wrong")',
                f'catch({ex_type}, "later")'
            ]
        elif case_type == 2:
            lines = [
                'try',
                f'throw({ex_type})',
                f'catch({other_ex}, "wrong")'
            ]
            correct_msg = "Unhandled Exception"
        
        program = []
        for line in lines:
            line = self._add_random_spaces(line)
            program.append(line)
        
        answer = self._compute_answer(program)
        return {
            'program': program,
            'answer': answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        program = question_case['program']
        program_text = '\n'.join(program)
        prompt = f"""你是Vasya编程语言（VPL）的测试员，请根据程序确定执行后的输出消息。

规则：
- 每个try必须对应一个catch。
- catch仅在异常类型匹配时触发，且其必须出现在throw之后。
- 多个符合条件的catch选择最内层且最早出现的。

程序：
{program_text}

请将答案放在[answer]和[/answer]之间。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _random_string(self, length):
        chars = string.ascii_letters
        return ''.join(random.choice(chars) for _ in range(length))

    def _add_random_spaces(self, line):
        parts = line.split('(', 1)
        operator = parts[0].strip()
        if len(parts) == 1:
            return f"{' ' * random.randint(0,2)}{operator}{' ' * random.randint(0,2)}"
        params = parts[1].rstrip(')').strip()
        params = re.sub(r'\s*,\s*', ', ', params)
        return f"{' ' * random.randint(0,2)}{operator}( {params} ){' ' * random.randint(0,2)}"

    def _compute_answer(self, program):
        class CheckExit(Exception):
            def __init__(self, msg):
                self.msg = msg

        def _check(tokens, target_ex, msg):
            if not tokens:
                return
            prev = tokens.pop()
            if prev == target_ex:
                raise CheckExit(msg)
            elif prev != 'TRY':
                _check(tokens, target_ex, msg)
                tokens.append(prev)
            else:
                tokens.append(prev)

        stack = []
        throw_ex = None
        for line in program:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped == 'try':
                stack.append('TRY')
            elif stripped.startswith('throw'):
                ex = stripped.split('(')[1].split(')')[0].strip()
                throw_ex = ex
                stack.append(ex)
            elif stripped.startswith('catch'):
                content = stripped.split('(', 1)[1].split(')', 1)[0].strip()
                ex, msg_part = content.split(',', 1)
                ex = ex.strip()
                msg = msg_part.strip().strip('"')
                temp_stack = stack.copy()
                try:
                    _check(temp_stack, ex, msg)
                except CheckExit as e:
                    return e.msg
                stack = temp_stack
        return "Unhandled Exception"
