import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class DthewuInstructionGenerator(BaseInstructionGenerator):
    """Dthewu Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dthewu指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', random.randint(2, 4))
        self.m = params.get('m', random.randint(5, 20))
        self.n = min(max(self.n, 1), 12)  # 确保n在合法范围
        self.m = min(max(self.m, 1), 10000)
    
    def case_generator(self):
        MAX_ATTEMPTS = 20
        n = self.n  # 定义局部变量避免self引用错误
        
        w = [random.randint(0, 100) for _ in range(n)]
        
        s_multiset = defaultdict(int)
        for _ in range(self.m):
            s = ''.join(random.choices('01', k=n))
            s_multiset[s] += 1
        
        valid_k = None
        for _ in range(MAX_ATTEMPTS):
            t = ''.join(random.choices('01', k=n))
            
            wu_counts = defaultdict(int)
            for s, cnt in s_multiset.items():
                xor = int(s, 2) ^ int(t, 2)
                # 修正变量作用域错误（原错误行）
                wu = sum(w[n - i - 1] for i in range(n) if (xor & (1 << i)) == 0)
                wu_counts[wu] += cnt
            
            sorted_wu = sorted(wu_counts.keys())
            if not sorted_wu:
                valid_k = 0
                break
            
            for candidate in [sorted_wu[len(sorted_wu)//2], 
                             sorted_wu[0] + (sorted_wu[-1]-sorted_wu[0])//3,
                             sorted_wu[-1]]:
                total = sum(cnt for wu, cnt in wu_counts.items() if wu <= candidate)
                if 0 < total < self.m:
                    valid_k = candidate
                    break
            if valid_k is not None:
                break
        
        if valid_k is None:
            valid_k = random.choice(sorted_wu) if sorted_wu else 0
        
        return {
            'n': n,
            'w': w,
            's_multiset': dict(s_multiset),
            't': t,
            'k': valid_k
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        problem_desc = [
            "## 谜题背景",
            "你需要帮助Childan验证'Dthewu'值阈值条件下的项链数量。每个01字符串的长度为n，每个位置的权重不同。",
            "\n## 参数说明",
            f"字符串长度 n = {question_case['n']}",
            f"权重数组 w = {question_case['w']}",
            "\n## 多集合S内容（字符串:出现次数）",
            *[f"- {s} × {cnt}" for s, cnt in question_case['s_multiset'].items()],
            "\n## 当前查询",
            f"目标字符串 t = {question_case['t']}",
            f"阈值 k = {question_case['k']}",
            "\n请计算满足条件的字符串总数，并将最终数值用[answer]标签包裹。"
        ]
        return '\n'.join(problem_desc) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

