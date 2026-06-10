import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from typing import Dict
from typing import Any
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple




class CsearchingforgraphInstructionGenerator(BaseInstructionGenerator):
    """Csearchingforgraph Bootcamp指令生成器"""
    
    def __init__(self, min_n: int = 5, max_n: int = 24, max_t: int = 5):
        """
        初始化Csearchingforgraph指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_t: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.max_t = max_t
    
    def case_generator(self) -> Dict[str, Any]:
        t = random.randint(1, self.max_t)
        tests = []
        for _ in range(t):
            n = random.randint(self.min_n, self.max_n)
            max_p = (n * (n - 1) // 2) - 2 * n
            if max_p < 0:
                max_p = 0  # Ensure p is non-negative
            p = random.randint(0, max_p)
            tests.append({'n': n, 'p': p})
        return {'tests': tests}
    
    @staticmethod
    def prompt_func(question_case: Dict[str, Any]) -> str:
        tests = question_case['tests']
        input_lines = [str(len(tests))]
        for test in tests:
            input_lines.append(f"{test['n']} {test['p']}")
        input_str = '\n'.join(input_lines)

        return f"""You are a programming expert. Solve the p-interesting graph construction problem.

**Problem Rules**:
1. The graph must contain exactly 2n + p edges (n = number of vertices)
2. No self-loops or duplicate edges
3. Any k-vertex subgraph (1 ≤ k ≤ n) must contain ≤ 2k + p edges

**Input Format**:
First line: t (number of test cases)
Next t lines: n and p values

**Output Format**:
For each test case, output 2n + p edges in any order

**Sample Input**:
1
6 0

**Sample Output**:
1 2
1 3
1 4
1 5
1 6
2 3
2 4
2 5
2 6
3 4
3 5
3 6

**Current Input**:
{input_str}

Place your answer between [answer] tags:
[answer]
{{your_answer}}
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

