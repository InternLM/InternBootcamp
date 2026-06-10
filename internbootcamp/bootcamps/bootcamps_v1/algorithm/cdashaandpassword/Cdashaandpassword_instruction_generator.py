import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random
import re




class CdashaandpasswordInstructionGenerator(BaseInstructionGenerator):
    """Cdashaandpassword Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cdashaandpassword指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化密码谜题训练场参数，确保参数范围有效性
        """
        super().__init__(**params)
        # 参数有效性约束（n≥3且m≥1）
        self.n = min(max(params.get('n', 3), 3), 50)
        self.m = max(params.get('m', 4), 1)
    
    def case_generator(self):
        """
        生成保证有效性的谜题实例（确保必然存在三种字符类型）
        """
        case = {
            "n": self.n,
            "m": self.m,
            "strings": []
        }
        
        # 生成必须包含数字的字符串（固定至少一个数字）
        s_digit = [random.choice('0123456789')]
        for _ in range(self.m-1):
            s_digit.append(random.choice('0123456789abcdefghijklmnopqrstuvwxyz#*&'))
        random.shuffle(s_digit)
        case["strings"].append(''.join(s_digit))
        
        # 生成必须包含小写字母的字符串（固定至少一个字母）
        s_alpha = [random.choice('abcdefghijklmnopqrstuvwxyz')]
        for _ in range(self.m-1):
            s_alpha.append(random.choice('0123456789abcdefghijklmnopqrstuvwxyz#*&'))
        random.shuffle(s_alpha)
        case["strings"].append(''.join(s_alpha))
        
        # 生成必须包含特殊符号的字符串（固定至少一个符号）
        s_special = [random.choice('#*&')]
        for _ in range(self.m-1):
            s_special.append(random.choice('0123456789abcdefghijklmnopqrstuvwxyz#*&'))
        random.shuffle(s_special)
        case["strings"].append(''.join(s_special))
        
        # 生成剩余字符串（随机类型）
        for _ in range(3, self.n):
            s = [
                random.choice('0123456789abcdefghijklmnopqrstuvwxyz#*&')
                for _ in range(self.m)
            ]
            case["strings"].append(''.join(s))
        
        return case
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        转换为符合题目输入格式的严格问题描述
        """
        return (
            "Dasha needs to set a password for programming class. The password must:\n"
            "1. Contain at least one digit (0-9)\n"
            "2. Contain at least one lowercase letter (a-z)\n"
            "3. Contain at least one of '#', '*' or '&'\n\n"
            "Each password character has a cyclic string. All pointers start at position 1.\n"
            "Find the minimal moves to form a valid password.\n\n"
            "Input format:\n"
            f"{question_case['n']} {question_case['m']}\n" +
            "\n".join(question_case['strings']) +
            "\n\nOutput the integer answer within [answer] tags like [answer]3[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

