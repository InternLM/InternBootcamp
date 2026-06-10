import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EzerooneInstructionGenerator(BaseInstructionGenerator):
    """Ezeroone Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ezeroone指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.min_length = params.get('min_length', 2)
        self.max_length = params.get('max_length', 105)
    
    def case_generator(self):
        n = random.randint(self.min_length, self.max_length)
        chars = ['0', '1', '?']
        case = ''.join(random.choices(chars, k=n))
        return {'initial': case}
    
    @staticmethod
    def prompt_func(question_case):
        initial = question_case['initial']
        prompt = f"""
        你是Masha和Petya的游戏分析师，请分析以下卡片序列：{initial}。其中，'?'表示该卡片的数字可以是0或1。游戏规则如下：

        玩家轮流移除卡片，直到剩下两张。Masha先手，她的目标是让最终的两位数尽可能小，而Petya的目标是尽可能大。对于所有可能的初始数字排列，请找出所有可能的最终结果，并按升序排列，每个结果放在单独的一行，格式为两位字符串。将答案放在[answer]标签中。

        例如，输入"1?1"的可能结果为01和11。
        """
        return prompt.strip() 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve(ea, eb, ua, ub, last_char):
        if ea >= eb + 1:
            return ['00']
        if ea + 2 <= eb:
            return ['11']
        if ea == eb or ea + 1 == eb:
            if last_char == '0':
                return ['10']
            elif last_char == '1':
                return ['01']
            elif last_char == '?':
                if ua > 0 and ub > 0:
                    return ['10', '01']
                elif ua > 0:
                    return ['10']
                elif ub > 0:
                    return ['01']
                else:
                    return []
            else:
                return []
        return []

    @staticmethod
    def compute_possible_outcomes(s):
        if not s:
            return []
        a = s.count('0')
        b = s.count('1')
        u = s.count('?')
        last_char = s[-1]
        results = set()
        for x in range(0, u + 1):
            ea = a + x
            eb = b + (u - x)
            outcome = Ezeroonebootcamp.solve(ea, eb, x, u - x, last_char)
            for o in outcome:
                results.add(o)
        return sorted(results)
