import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
import string
from collections import deque

# === 源文件中的全局函数 ===

def process_word(s):
    """严格遵循题目参考代码的处理逻辑"""
    ans = ["!", "@"]
    for char in s:
        while len(ans) >= 3 and (char == ans[-1] == ans[-2] or char == ans[-1] and ans[-3] == ans[-2]):
            ans.pop()
        ans.append(char)
    return ''.join(ans[2:])


class CfixingtyposInstructionGenerator(BaseInstructionGenerator):
    """Cfixingtypos Bootcamp指令生成器"""
    
    def __init__(self, min_length=6, max_length=200):
        """
        初始化Cfixingtypos指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_length = max(6, min_length)  # 确保最小有效长度
        self.max_length = min(max_length, 20000)  # 遵循题目输入约束
    
    def case_generator(self):
        """生成保证包含至少一个有效错误的测试用例"""
        error_type = random.choice([1, 2, 1, 2])  # 增加类型1的概率
        s = []

        # 生成基础字符流（保证无预存错误）
        base_chars = [
            c for c in random.choices(string.ascii_lowercase, 
            k=random.randint(self.min_length-3, self.max_length))
            if len(s) < 1 or c != s[-1]  # 防止自然产生连续对
        ]

        # 插入错误模式
        if error_type == 1:  # 三连字符
            insert_pos = random.randint(0, len(base_chars)-1)
            c = base_chars[insert_pos] if random.random() < 0.5 else random.choice(string.ascii_lowercase)
            error = [c]*3
        else:  # 连续重复对
            pairs = [random.choice(string.ascii_lowercase) for _ in range(2)]
            error = pairs*2 if random.random() < 0.5 else [pairs[0]]*2 + [pairs[1]]*2

        # 将错误模式插入随机位置
        insert_pos = random.randint(0, len(base_chars))
        s = base_chars[:insert_pos] + error + base_chars[insert_pos:]

        # 转换为字符串并校验有效性
        s = ''.join(s[:self.max_length])
        t = process_word(s)

        # 确保生成有效错误
        if len(t) >= len(s):  # 重新生成直到产生有效错误
            return self.case_generator()

        return {
            'input': s,
            'correct_length': len(t),
            '_ref_solution': t  # 调试用
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""作为文本处理专家，请修正以下单词中的打字错误：

输入单词: {question_case['input']}

修正规则：
1. 删除最少数量的字符
2. 不允许三个连续相同字母（如"baaaad"→"baad"）
3. 不允许两组连续重复对相邻（如"wooooooow"→"woow"）

请将最终答案放在[answer]标签内，例如：[answer]corrected[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

