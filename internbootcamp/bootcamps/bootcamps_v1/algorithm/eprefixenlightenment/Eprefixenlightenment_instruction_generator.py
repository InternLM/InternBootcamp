import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class EprefixenlightenmentInstructionGenerator(BaseInstructionGenerator):
    """Eprefixenlightenment Bootcamp指令生成器"""
    
    def __init__(self, n=5, k=3):
        """
        初始化Eprefixenlightenment指令生成器
        
        Args:
            n: 参数描述
            k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if k > 2 * n:
            raise ValueError("k must be <= 2*n to ensure valid subset generation.")
        self.n = n
        self.k = k
    
    def case_generator(self):
        n, k = self.n, self.k
        element_counters = defaultdict(int)
        subsets = []
        for _ in range(k):
            available = [x for x in range(1, n+1) if element_counters[x] < 2]
            if not available:
                break  # 简化处理，实际可能需要更鲁棒的生成逻辑
            x = random.choice(available)
            subsets.append([x])
            element_counters[x] += 1
        
        S = random.sample(range(k), random.randint(0, k))
        count_in_S = defaultdict(int)
        for j in S:
            x = subsets[j][0]
            count_in_S[x] += 1
        
        s_str = ''.join(['1' if (count_in_S[i] % 2 == 0) else '0' for i in range(1, n+1)])
        
        # 此处的正确m_i计算需要实现参考代码逻辑，此处简化为mock数据
        correct_mi = [0] * n  # 此处应替换为正确计算
        
        return {
            'n': n,
            'k': k,
            'initial_state': s_str,
            'subsets': subsets,
            'correct_mi': correct_mi,
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        s = question_case['initial_state']
        subsets = question_case['subsets']
        
        prompt = (
            f"There are {n} lamps in a line, numbered 1 to {n}. Initial states: {s}\n"
            f"Available {k} subsets (any three intersect empty):\n"
        )
        for idx, subset in enumerate(subsets, 1):
            prompt += f"- Subset {idx}: {subset}\n"
        prompt += (
            "\nTask: For each 1 ≤ i ≤ {n}, compute m_i - the minimal operations to make lamps 1-i all on.\n"
            "Output format: n lines each containing m_i. Enclose answers in [answer]...[/answer]."
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

