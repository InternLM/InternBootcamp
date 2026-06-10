import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from math import gcd
from collections import defaultdict




class CdilucandkaeyaInstructionGenerator(BaseInstructionGenerator):
    """Cdilucandkaeya Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cdilucandkaeya指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        # 参数处理增强：允许动态配置字符串长度范围和特殊模式概率
        self.min_length = params.get('min_length', 1)
        self.max_length = params.get('max_length', 10)
        self.special_prob = params.get('special_prob', 0.2)  # 全D/K的概率
    
    def case_generator(self):
        # 生成更丰富的测试用例（包含全D、全K、混合情况）
        if random.random() < self.special_prob:
            # 生成特殊模式
            char = random.choice(['D', 'K'])
            n = random.randint(self.min_length, self.max_length)
            s = char * n
        else:
            # 正常随机生成
            n = random.randint(self.min_length, self.max_length)
            s = ''.join(random.choices(['D','K'], k=n))
        
        # 严格遵循问题示例的数据结构
        return {'n': n, 's': s}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        # 构造精确匹配问题描述的prompt
        return f"""给定长度为{question_case['n']}的字符串s={question_case['s']}，对每个前缀s[1..i]（1 ≤ i ≤ {question_case['n']}），输出最大分割块数使得每块的D:K比例相同。将答案用空格分隔放在[answer]标签内，如：[answer]1 2 3[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

