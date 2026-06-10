import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class BmultithreadingInstructionGenerator(BaseInstructionGenerator):
    """Bmultithreading Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=20):
        """
        初始化Bmultithreading指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        """生成符合题意的随机测试用例"""
        n = random.randint(self.min_n, self.max_n)
        a = list(range(1, n+1))
        random.shuffle(a)
        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        """准确传递输入数据的自然语言问题描述"""
        n = question_case['n']
        a_str = ' '.join(map(str, question_case['a']))  # 关键修复：不要反转数组
        return f"""你正在帮助Emuskald分析Codeforces的最近活动列表。列表中有n个不同的线程，当某个线程收到新消息时，它会跳到列表最前面。现在列表顺序已更新，已知刷新后的第i个位置(1≤i≤n)对应的线程在刷新前的位置是a_i（所有a_i构成1到n的排列）。

输入格式：
第一行：整数n
第二行：n个互不相同的整数a_1到a_n（1≤a_i≤n）

当前测试用例：
n = {n}
a = {a_str}

请严格按以下步骤分析：
1. 识别所有必须包含新消息的线程
2. 将答案的整数值放在[answer]和[/answer]之间，例如：[answer]3[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

