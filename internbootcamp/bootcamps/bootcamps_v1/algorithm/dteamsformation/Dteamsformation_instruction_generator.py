import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class DteamsformationInstructionGenerator(BaseInstructionGenerator):
    """Dteamsformation Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dteamsformation指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = params.get('max_n', 100)
        self.max_k = params.get('max_k', 100)
        self.max_m = params.get('max_m', 100)
        self.city_max = params.get('city_max', 50)
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        k = random.randint(2, self.max_k)
        m = random.randint(1, self.max_m)
        a = [random.randint(1, self.city_max) for _ in range(n)]
        return {'n': n, 'k': k, 'm': m, 'a': a}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        case = question_case
        input_lines = f"{case['n']} {case['k']} {case['m']}\n{' '.join(map(str, case['a']))}"
        return f"""根据以下规则解决问题：
[规则]
1. 巴士往返m次形成总队列
2. 移除所有连续的k个同城参与者
3. 返回最终剩余人数

[输入]
{input_lines}

答案放入[answer]标签内，如：[answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

