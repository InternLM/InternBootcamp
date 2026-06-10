import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import html




class ElogicalexpressionInstructionGenerator(BaseInstructionGenerator):
    """Elogicalexpression Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Elogicalexpression指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
    
    def case_generator(self):
        ans = self._get_ans_list()
        import random
        index = random.randint(0, len(ans)-1)
        truth_table = bin(index)[2:].zfill(8)
        return {'truth_table': truth_table}
    
    @staticmethod
    def prompt_func(question_case):
        truth_table = question_case['truth_table']
        prompt = f"""你是一位逻辑电路专家，需要解决一个布尔函数的最简表达式问题。给定的布尔函数有三个变量x、y、z，其真值表如下：

真值表：{truth_table}

真值表的每一位对应输入的三变量的二进制组合的结果。其中，第0位对应x=0,y=0,z=0时的结果；第1位对应x=0,y=0,z=1时的结果；依此类推，直到第7位对应x=1,y=1,z=1时的结果。

任务要求：
1. 找出与该真值表对应的布尔表达式，该表达式必须由变量x、y、z，运算符&（AND）、|（OR）、!（NOT）以及括号构成。
2. 表达式必须尽可能短，即使用最少的字符数。如果有多个最短表达式，选择字典序最小的一个。
3. 运算符的优先级为：NOT > AND > OR，必要时使用括号改变优先级。
4. 表达式必须符合特定的语法规则，不允许有多余的空格或其他字符。

请根据上述规则，给出该布尔函数的最简表达式，并将答案放在[answer]和[/answer]标签之间。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _get_ans_list():
        return [
            '!x&x', 'x&y&z', '!z&x&y', 'x&y', '!y&x&z', 'x&z', '!y&x&z|!z&x&y', '(y|z)&x', '!y&!z&x', '!y&!z&x|x&y&z',
            '!z&x', '!z&x|x&y', '!y&x', '!y&x|x&z', '!(y&z)&x', 'x', '!x&y&z', 'y&z', '!x&y&z|!z&x&y', '(x|z)&y',
            '!x&y&z|!y&x&z', '(x|y)&z', '!x&y&z|!y&x&z|!z&x&y', '(x|y)&z|x&y', '!x&y&z|!y&!z&x', '!y&!z&x|y&z',
            '!x&y&z|!z&x', '!z&x|y&z', '!x&y&z|!y&x', '!y&x|y&z', '!(y&z)&x|!x&y&z', 'x|y&z', '!x&!z&y',
            '!x&!z&y|x&y&z', '!z&y', '!z&y|x&y', '!x&!z&y|!y&x&z', '!x&!z&y|x&z', '!y&x&z|!z&y', '!z&y|x&z',
            '!(!x&!y|x&y|z)', '!(!x&!y|x&y|z)|x&y&z', '!z&(x|y)', '!z&(x|y)|x&y', '!x&!z&y|!y&x',
            '!x&!z&y|!y&x|x&z', '!y&x|!z&y', '!z&y|x', '!x&y', '!x&y|y&z', '!(x&z)&y', 'y', '!x&y|!y&x&z',
            '!x&y|x&z', '!(x&z)&y|!y&x&z', 'x&z|y', '!x&y|!y&!z&x', '!x&y|!y&!z&x|y&z', '!x&y|!z&x', '!z&x|y',
            '!x&y|!y&x', '!x&y|!y&x|x&z', '!(x&z)&y|!y&x', 'x|y', '!x&!y&z', '!x&!y&z|x&y&z', '!x&!y&z|!z&x&y',
            '!x&!y&z|x&y', '!y&z', '!y&z|x&z', '!y&z|!z&x&y', '!y&z|x&y', '!(!x&!z|x&z|y)', '!(!x&!z|x&z|y)|x&y&z',
            '!x&!y&z|!z&x', '!x&!y&z|!z&x|x&y', '!y&(x|z)', '!y&(x|z)|x&z', '!y&z|!z&x', '!y&z|x', '!x&z',
            '!x&z|y&z', '!x&z|!z&x&y', '!x&z|x&y', '!(x&y)&z', 'z', '!(x&y)&z|!z&x&y', 'x&y|z', '!x&z|!y&!z&x',
            '!x&z|!y&!z&x|y&z', '!x&z|!z&x', '!x&z|!z&x|x&y', '!x&z|!y&x', '!y&x|z', '!(x&y)&z|!z&x', 'x|z',
            '!(!y&!z|x|y&z)', '!(!y&!z|x|y&z)|x&y&z', '!x&!y&z|!z&y', '!x&!y&z|!z&y|x&y', '!x&!z&y|!y&z',
            '!x&!z&y|!y&z|x&z', '!y&z|!z&y', '!y&z|!z&y|x&y', '!(!x&!y|x&y|z)|!x&!y&z', '!(!x&!y|x&y|z)|!x&!y&z|x&y&z',
            '!x&!y&z|!z&(x|y)', '!x&!y&z|!z&(x|y)|x&y', '!x&!z&y|!y&(x|z)', '!x&!z&y|!y&(x|z)|x&z', '!y&(x|z)|!z&y',
            '!y&z|!z&y|x', '!x&(y|z)', '!x&(y|z)|y&z', '!x&z|!z&y', '!x&z|y', '!x&y|!y&z', '!x&y|z', '!(x&y)&z|!z&y',
            'y|z', '!x&(y|z)|!y&!z&x', '!x&(y|z)|!y&!z&x|y&z', '!x&(y|z)|!z&x', '!x&z|!z&x|y', '!x&(y|z)|!y&x',
            '!x&y|!y&x|z', '!x&y|!y&z|!z&x', 'x|y|z', '!(x|y|z)', '!(x|y|z)|x&y&z', '!(!x&y|!y&x|z)', '!(x|y|z)|x&y',
            '!(!x&z|!z&x|y)', '!(x|y|z)|x&z', '!(!x&y|!y&x|z)|!y&x&z', '!(x|y|z)|(y|z)&x', '!y&!z', '!y&!z|x&y&z',
            '!(!x&y|z)', '!y&!z|x&y', '!(!x&z|y)', '!y&!z|x&z', '!(!x&y|z)|!y&x', '!y&!z|x', '!(!y&z|!z&y|x)',
            '!(x|y|z)|y&z', '!(!x&y|!y&x|z)|!x&y&z', '!(x|y|z)|(x|z)&y', '!(!x&z|!z&x|y)|!x&y&z', '!(x|y|z)|(x|y)&z',
            '!(!x&y|!y&x|z)|!x&y&z|!y&x&z', '!(x|y|z)|(x|y)&z|x&y', '!x&y&z|!y&!z', '!y&!z|y&z', '!(!x&y|z)|!x&y&z',
            '!(!x&y|z)|y&z', '!(!x&z|y)|!x&y&z', '!(!x&z|y)|y&z', '!(!x&y|z)|!x&y&z|!y&x', '!y&!z|x|y&z', '!x&!z',
            '!x&!z|x&y&z', '!(!y&x|z)', '!x&!z|x&y', '!x&!z|!y&x&z', '!x&!z|x&z', '!(!y&x|z)|!y&x&z', '!(!y&x|z)|x&z',
            '!(x&y|z)', '!(x&y|z)|x&y&z', '!z', '!z|x&y', '!x&!z|!y&x', '!(x&y|z)|x&z', '!y&x|!z', '!z|x',
            '!(!y&z|x)', '!x&!z|y&z', '!(!y&x|z)|!x&y', '!x&!z|y', '!(!y&z|x)|!y&x&z', '!(!y&z|x)|x&z',
            '!(!y&x|z)|!x&y|!y&x&z', '!x&!z|x&z|y', '!x&y|!y&!z', '!(x&y|z)|y&z', '!x&y|!z', '!z|y',
            '!(!x&!y&z|x&y)', '!x&!z|!y&x|y&z', '!x&y|!y&x|!z', '!z|x|y', '!x&!y', '!x&!y|x&y&z', '!x&!y|!z&x&y',
            '!x&!y|x&y', '!(!z&x|y)', '!x&!y|x&z', '!(!z&x|y)|!z&x&y', '!(!z&x|y)|x&y', '!(x&z|y)', '!(x&z|y)|x&y&z',
            '!x&!y|!z&x', '!(x&z|y)|x&y', '!y', '!y|x&z', '!y|!z&x', '!y|x', '!(!z&y|x)', '!x&!y|y&z',
            '!(!z&y|x)|!z&x&y', '!(!z&y|x)|x&y', '!(!z&x|y)|!x&z', '!x&!y|z', '!(!z&x|y)|!x&z|!z&x&y',
            '!x&!y|x&y|z', '!x&z|!y&!z', '!(x&z|y)|y&z', '!(!x&!z&y|x&z)', '!x&!y|!z&x|y&z', '!x&z|!y', '!y|z',
            '!x&z|!y|!z&x', '!y|x|z', '!(x|y&z)', '!(x|y&z)|x&y&z', '!x&!y|!z&y', '!(x|y&z)|x&y', '!x&!z|!y&z',
            '!(x|y&z)|x&z', '!(!y&!z&x|y&z)', '!x&!y|!z&y|x&z', '!((x|y)&z|x&y)', '!((x|y)&z|x&y)|x&y&z', '!x&!y|!z',
            '!x&!y|!z|x&y', '!x&!z|!y', '!x&!z|!y|x&z', '!y|!z', '!y|!z|x', '!x', '!x|y&z', '!x|!z&y', '!x|y',
            '!x|!y&z', '!x|z', '!x|!y&z|!z&y', '!x|y|z', '!x|!y&!z', '!x|!y&!z|y&z', '!x|!z', '!x|!z|y', '!x|!y',
            '!x|!y|z', '!(x&y&z)', '!x|x'
        ]
