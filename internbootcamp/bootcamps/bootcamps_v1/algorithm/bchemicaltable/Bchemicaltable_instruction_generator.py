import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from typing import Set
from typing import Tuple




class BchemicaltableInstructionGenerator(BaseInstructionGenerator):
    """Bchemicaltable Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=10):
        """
        初始化Bchemicaltable指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        增强初始化参数校验，确保行列数合法
        Args:
            max_n: 行数的最大值 (≥1)
            max_m: 列数的最大值 (≥1)
        """
        self.max_n = max(max_n, 1)
        self.max_m = max(max_m, 1)
    
    def case_generator(self) -> dict:
        """
        生成健壮的测试案例，覆盖所有边界条件
        返回结构：{'n', 'm', 'q', 'elements', 'correct_answer'}
        """
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        max_q = n * m
        
        # 控制q的分布，提高边界条件概率
        q_options = [
            0, 1, 
            max_q//2, 
            max_q-1, 
            max_q,
            random.randint(0, max_q)
        ]
        q = random.choice(q_options)
        
        # 生成元素时优先覆盖行列边界
        elements: Set[Tuple[int, int]] = set()
        while len(elements) < q:
            # 优先生成边角元素增加连通可能性
            if random.random() < 0.3 and n > 1 and m > 1:
                r = random.choice([1, n])
                c = random.choice([1, m])
            else:
                r = random.randint(1, n)
                c = random.randint(1, m)
            elements.add((r, c))
        
        # 并查集初始化（1~n为行节点，n+1~n+m为列节点）
        parent = list(range(n + m + 1))  # 索引0未使用
        
        def find(u: int) -> int:
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u
        
        initial_components = n + m
        res = initial_components - 1  # 最小生成树边数
        
        for r, c in elements:
            u = r
            v = n + c
            fu = find(u)
            fv = find(v)
            if fu != fv:
                parent[fu] = fv
                res -= 1
        
        return {
            'n': n,
            'm': m,
            'q': q,
            'elements': list(elements),
            'correct_answer': max(res, 0)  # 结果非负
        }
    
    @staticmethod
    def prompt_func(question_case: dict) -> str:
        """
        生成标准化问题描述，明确输入输出格式
        """
        elements = question_case['elements']
        elements_desc = (
            "科学家目前尚未拥有任何元素的样本。" 
            if question_case['q'] == 0 else
            "初始拥有的元素坐标为：\n" + 
            '\n'.join(f"{r} {c}" for r, c in elements)
        )
        
        return f"""## 化学元素合成问题

**表格结构**: {question_case['n']} 行 × {question_case['m']} 列
**已有元素**: {question_case['q']} 个
{elements_desc}

**规则**: 若存在矩形的三个角元素，可合成第四个。合成出的元素可继续用于后续合成。

**任务**: 计算需要购入的最小元素数量，使得能通过合成获得所有元素。

**答案格式**: 将最终整数答案置于[answer]标签内，例如：[answer]0[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

