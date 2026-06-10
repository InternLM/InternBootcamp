import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class CfixingtyposRewardCalculator(BaseRewardCalculator):
    """Cfixingtypos奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 基础格式检查
        if not isinstance(solution, str) or not solution.isalpha():
            return False
        
        # 长度校验
        if len(solution) != identity['correct_length']:
            return False
        
        # 子序列验证
        src = deque(identity['input'])
        try:
            for c in solution:
                while src.popleft() != c:
                    pass
        except IndexError:
            return False

        # 错误模式检查
        # 三级联检查
        for i in range(len(solution)-2):
            if solution[i] == solution[i+1] == solution[i+2]:
                return False
        
        # 连续两对检查
        for i in range(len(solution)-3):
            if solution[i] == solution[i+1] and solution[i+2] == solution[i+3]:
                return False

        return True
    
    # 其他额外方法

