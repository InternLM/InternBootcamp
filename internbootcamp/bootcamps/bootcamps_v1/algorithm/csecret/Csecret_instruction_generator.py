import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CsecretInstructionGenerator(BaseInstructionGenerator):
    """Csecret Bootcamp指令生成器"""
    
    def __init__(self, max_k=20, max_n=200, unsolvable_ratio=0.3):
        """
        初始化Csecret指令生成器
        
        Args:
            max_k: 参数描述
            max_n: 参数描述
            unsolvable_ratio: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数说明:
            max_k: 最大守护者数 (默认20)
            max_n: 最大单词数 (默认200)
            unsolvable_ratio: 强制生成不可解案例的概率 (0.3)
        """
        self.max_k = max_k
        self.max_n = max_n
        self.unsolvable_ratio = unsolvable_ratio
    
    def case_generator(self):
        # 控制不可解案例生成
        if random.random() < self.unsolvable_ratio:
            k = random.randint(2, self.max_k//2)
            n = random.randint(k, 3*k -1)  # 确保3k >n
        else:
            k = random.randint(2, self.max_k)
            min_n = 3*k
            n = random.randint(min_n, min(min_n + 50, self.max_n))  # 生成有效解附近的值
        
        return {'n': n, 'k': k}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        return f"""你需要将{n}个单词分配给{k}位守护者，满足：
1. 每个守护者获得≥3个单词
2. 所有守护者的单词集合互不相交
3. 所有单词必须分配
4. 每个守护者的单词编号不能形成等差数列

输入：n={n} k={k}

若存在解决方案，输出{n}个1~{k}的整数（空格分隔）；否则输出-1。答案置于[answer][/answer]中。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

