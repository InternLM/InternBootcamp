import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class ApetyaandcatacombsInstructionGenerator(BaseInstructionGenerator):
    """Apetyaandcatacombs Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10):
        """
        初始化Apetyaandcatacombs指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        """严格符合ti < i约束的案例生成"""
        n = random.randint(self.min_n, self.max_n)
        return {
            'n': n,
            't': [random.randint(0, i-1) for i in range(1, n+1)]
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        t_values = ' '.join(map(str, question_case['t']))
        return f"""你是地下墓穴路径分析专家，需要根据Petya的移动日志确定最小房间数。以下是任务详情：

## 背景规则
1. 每分钟移动到相邻房间
2. 新房间：记录任意小于当前时间的数
3. 旧房间：记录上次访问时间

## 输入案例
第一行（房间数）：{n}
第二行（时间序列）：{t_values}

## 答案要求
将最终答案放在[answer]标签内，如：[answer]5[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

