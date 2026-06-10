import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

max_length = 100

max_sum = max_length * 26

dp = [[0] * (max_sum + 1) for _ in range(max_length + 1)]

dp[0][0] = 1


class EcipherInstructionGenerator(BaseInstructionGenerator):
    """Ecipher Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ecipher指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_len = params.get('min_len', 1)
        self.max_len = params.get('max_len', 100)
        super().__init__(**params)
    
    def case_generator(self):
        """生成包含特殊边界案例的测试数据"""
        # 10%概率生成特殊案例
        if random.random() < 0.1:
            n = random.randint(self.min_len, self.max_len)
            # 生成全a或全z的极端情况
            word = random.choice([
                'a' * n,
                'z' * n,
                'a' + 'z'*(n-1) if n > 1 else 'a'
            ])
        else:
            n = random.randint(self.min_len, self.max_len)
            word = ''.join(random.choices(string.ascii_lowercase, k=n))
        return {"word": word}
    
    @staticmethod
    def prompt_func(question_case):
        word = question_case['word']
        return f"""请解决以下加密问题：
给定单词 "{word}"，计算可以通过合法操作转换得到的不同单词数量（需与原单词不同）。答案需为整数，并置于[answer]标签内。

操作规则：
1. 每次操作选择相邻两个字符(p和p+1)
2. 两种可选操作：
   a) p字符后移 + p+1字符前移
   b) p字符前移 + p+1字符后移
3. 非法操作示例：a不能前移，z不能后移

答案格式示例：[answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

