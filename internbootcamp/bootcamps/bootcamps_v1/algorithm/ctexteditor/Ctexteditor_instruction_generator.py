import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CtexteditorInstructionGenerator(BaseInstructionGenerator):
    """Ctexteditor Bootcamp指令生成器"""
    
    def __init__(self, min_lines=2, max_lines=100, max_chars=10**5):
        """
        初始化Ctexteditor指令生成器
        
        Args:
            min_lines: 参数描述
            max_lines: 参数描述
            max_chars: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_lines = min_lines
        self.max_lines = max_lines
        self.max_chars = max_chars
    
    def case_generator(self):
        n = random.randint(self.min_lines, self.max_lines)
        
        a = []
        for _ in range(n):
            if random.random() < 0.3:
                a.append(0)
            else:
                a.append(random.randint(0, self.max_chars))
        
        if random.random() < 0.5:
            r1 = r2 = random.randint(1, n)
        else:
            r1, r2 = random.sample(range(1, n+1), 2)
        
        max_c1 = a[r1-1] + 1
        c1 = random.randint(1, max(max_c1, 1))
        max_c2 = a[r2-1] + 1
        c2 = random.randint(1, max(max_c2, 1))
        
        return {
            'n': n,
            'a': a,
            'r1': r1,
            'c1': c1,
            'r2': r2,
            'c2': c2
        }
    
    @staticmethod
    def prompt_func(question_case):
        a_desc = []
        for idx, val in enumerate(question_case['a']):
            a_desc.append(f"第{idx+1}行：{val}字符（共{val+1}个光标位）")
        
        line_desc = '\n'.join(a_desc)
        
        prompt = f"""## 光标移动最小按键次数问题
文本编辑器共有{question_case['n']}行，各行的字符数如下：
{line_desc}

### 起始位置
- 行号：{question_case['r1']}
- 列号：{question_case['c1']}

### 目标位置
- 行号：{question_case['r2']}
- 列号：{question_case['c2']}

### 移动规则
1. 上下移动保持列号，若目标行不足该列则移动到行尾
2. 左右移动单步调整列号，无法越界移动

请计算最少按键次数，并将最终答案用[answer]标签包裹。"""

        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

