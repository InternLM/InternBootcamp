import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import math




class CdevelopingskillsInstructionGenerator(BaseInstructionGenerator):
    """Cdevelopingskills Bootcamp指令生成器"""
    
    def __init__(self, max_n=1000, max_k=10**6, max_a=100):
        """
        初始化Cdevelopingskills指令生成器
        
        Args:
            max_n: 参数描述
            max_k: 参数描述
            max_a: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max(max_n, 1)
        self.max_k = max(max_k, 0)
        self.max_a = min(max_a, 100)
    
    def case_generator(self):
        if random.random() < 0.2:
            return self._generate_edge_case()
        
        n = random.randint(1, self.max_n)
        k = random.randint(0, self.max_k)
        a_list = [random.randint(0, self.max_a) for _ in range(n)]
        
        if random.random() < 0.3 and n > 0:
            a_list[random.randint(0, n-1)] = 100
        
        return {
            'n': n,
            'k': k,
            'a_list': a_list,
            'correct_output': self._calculate_solution(n, k, a_list)
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        a_str = ' '.join(map(str, question_case['a_list']))
        prompt = (
            "## 游戏角色技能优化问题\n\n"
            "### 规则说明\n"
            "1. 每个技能值ai（0-100）对应评分⌊ai/10⌋\n"
            "2. 可用k个改进单位（每个+1技能值，不超过100）\n"
            "3. 求最大总评分\n\n"
            f"输入：n={n}, k={k}, 初始值=[{a_str}]\n"
            "输出格式：[answer]答案[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_edge_case(self):
        case_type = random.choice([
            'max_skills', 'zero_improvements', 'all_maxed', 
            'large_k', 'minimum_values'
        ])

        if case_type == 'max_skills':
            return {
                'n': self.max_n,
                'k': self.max_k,
                'a_list': [100] * self.max_n,
                'correct_output': 10 * self.max_n
            }
        elif case_type == 'zero_improvements':
            a_list = [random.randint(0, 100) for _ in range(random.randint(1, self.max_n))]
            return {
                'n': len(a_list),
                'k': 0,
                'a_list': a_list,
                'correct_output': sum(x//10 for x in a_list)
            }
        elif case_type == 'all_maxed':
            n = random.randint(1, self.max_n)
            return {
                'n': n,
                'k': random.randint(0, self.max_k),
                'a_list': [100]*n,
                'correct_output': 10*n
            }
        elif case_type == 'large_k':
            n = random.randint(1, 100)
            return {
                'n': n,
                'k': 10**7,
                'a_list': [0]*n,
                'correct_output': min(10*n, (sum(0//10 for _ in range(n)) + 10**7//10))
            }
        else:
            return {
                'n': 1,
                'k': 0,
                'a_list': [0],
                'correct_output': 0
            }

    @staticmethod
    def _calculate_solution(n, k, a_list):
        total = sum(x // 10 for x in a_list)
        remainder_counts = [0] * 10  # 索引对应delta值1-9（0位置不使用）

        for x in a_list:
            rem = x % 10
            if rem != 0:
                delta = 10 - rem
                if 1 <= delta <= 9:
                    remainder_counts[delta] += 1

        # 按delta从大到小处理（9到1）
        for delta in range(9, 0, -1):
            if k <= 0:
                break
            count = remainder_counts[delta]
            if count == 0:
                continue

            max_possible = min(k // delta, count)
            total += max_possible
            k -= max_possible * delta

        # 处理剩余k值
        total += k // 10
        return min(total, 10 * n)
