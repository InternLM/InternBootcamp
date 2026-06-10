import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

MAX_FIB_LENGTH = 10**5 + 10  # 覆盖题目最大输入长度


class CconstanzesmachineInstructionGenerator(BaseInstructionGenerator):
    """Cconstanzesmachine Bootcamp指令生成器"""
    
    def __init__(self, min_length=3, max_length=100, prob_wm=0.3, prob_error=0.2):
        """
        初始化Cconstanzesmachine指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
            prob_wm: 参数描述
            prob_error: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_length = max(min_length, 1)
        self.max_length = min(max_length, 1000)  # 控制生成规模
        self.prob_wm = prob_wm
        self.prob_error = prob_error
    
    def case_generator(self):
        while True:
            # Phase 1: 生成合法原始字符串
            original = []
            required_length = random.randint(self.min_length, self.max_length)
            
            while len(original) < required_length:
                # 优先注入特殊字符（w/m）
                if random.random() < self.prob_wm:
                    c = random.choice(['w', 'm'])
                    original.append(c)
                    continue
                
                # 生成常规字符（允许u/n但不连续）
                valid_chars = [chr(ord('a') + i) for i in range(26)]
                if original:
                    last_char = original[-1]
                    if last_char == 'u' and 'u' in valid_chars:
                        valid_chars.remove('u')
                    elif last_char == 'n' and 'n' in valid_chars:
                        valid_chars.remove('n')
                
                c = random.choice(valid_chars)
                original.append(c)
            
            # 转换为受控字符串
            s = ''.join(original).replace('w', 'uu').replace('m', 'nn')
            
            # Phase 2: 注入错误字符（如果需要）
            if random.random() < self.prob_error:
                error_pos = random.randint(0, len(s)-1)
                s = s[:error_pos] + random.choice(['m', 'w']) + s[error_pos+1:]
            
            # 合法性检查
            if self.min_length <= len(s) <= self.max_length:
                return {'s': s}
    
    @staticmethod
    def prompt_func(question_case):
        s = question_case['s']
        return (
            f"Analyze the string '{s}' according to Cconstanzesmachine's machine rules:\n"
            "1. Original characters are transformed as: w→uu, m→nn\n"
            "2. Input containing 'w'/'m' is invalid (output 0)\n"
            "3. Count possible source strings modulo 1e9+7\n\n"
            "Format: [answer]NUMBER[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

