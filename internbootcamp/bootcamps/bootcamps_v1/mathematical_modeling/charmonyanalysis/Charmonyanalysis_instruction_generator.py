import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CharmonyanalysisInstructionGenerator(BaseInstructionGenerator):
    """Charmonyanalysis Bootcamp指令生成器"""
    
    def __init__(self, min_k=0, max_k=9):
        """
        初始化Charmonyanalysis指令生成器
        
        Args:
            min_k: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if min_k < 0 or max_k > 9:
            raise ValueError("k must be between 0 and 9 inclusive.")
        self.min_k = min_k
        self.max_k = max_k
    
    def case_generator(self):
        k = random.randint(self.min_k, self.max_k)
        return {"k": k}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        k = question_case["k"]
        n = 2 ** k
        example = (
            "++**\n"
            "+*+*\n"
            "++++\n"
            "+**+"
        ) if k == 2 else ("+" if k == 0 else "")
        prompt = f"""You are tasked with solving a mathematical puzzle involving orthogonal vectors in a {n}-dimensional space. 

**Problem Statement:**
Find 2^{k} vectors in a 2^{k}-dimensional space where each coordinate is either +1 or -1, such that every pair of distinct vectors is orthogonal. Two vectors are orthogonal if their dot product equals zero.

**Input Specification:**
- The integer k is {k} (0 ≤ k ≤ 9).

**Output Format:**
- Print 2^{k} lines, each containing 2^{k} characters.
- Use '+' for +1 and '*' for -1.
  
**Example for k=2:**
{example}

**Answer Submission:**
Place your final answer between [answer] and [/answer] tags. Each vector must be on a separate line."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

