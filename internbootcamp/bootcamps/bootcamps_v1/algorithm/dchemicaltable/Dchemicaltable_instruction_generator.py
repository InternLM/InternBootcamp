import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DchemicaltableInstructionGenerator(BaseInstructionGenerator):
    """Dchemicaltable Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_m=5, max_q=200000):
        """
        初始化Dchemicaltable指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_q: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max(max_n, 1)
        self.max_m = max(max_m, 1)
        self.max_q = min(abs(max_q), 200000)
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        max_possible_q = n * m
        
        # 优化大q值生成效率
        if self.max_q < max_possible_q // 2:
            # 随机生成模式
            q = random.randint(0, min(self.max_q, max_possible_q))
            elements = set()
            while len(elements) < q:
                elements.add((random.randint(1, n), random.randint(1, m)))
        else:
            # 全量生成后随机删除
            all_elements = [(r, c) for r in range(1, n+1) for c in range(1, m+1)]
            random.shuffle(all_elements)
            q = random.randint(max(0, len(all_elements) - self.max_q), len(all_elements))
            elements = set(all_elements[:q])
        
        return {
            'n': n,
            'm': m,
            'elements': [[r, c] for r, c in sorted(elements)]
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        elements = question_case['elements']
        
        # 多语言问题描述支持
        element_desc = (
            "科学家已拥有以下元素样本：{}\n"
            if elements else 
            "实验室目前没有任何初始样本。\n"
        ).format(', '.join(f"第{r}行第{c}列" for r, c in elements)) if elements else ""
        
        return f"""## 元素合成问题
你正在管理一个{n}行{m}列的元素周期表实验室。{element_desc}
根据最新研究成果，当存在三个元素形成矩形顶点时，可以合成第四个顶点元素（合成过程不消耗原材料）。

**任务**：确定实验室至少需要购买多少新元素才能通过合成获得所有{n*m}个元素。

**输出要求**：将最终答案放在[answer]标签内，如：[answer]3[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

