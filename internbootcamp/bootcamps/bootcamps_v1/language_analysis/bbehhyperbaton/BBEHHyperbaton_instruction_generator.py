import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import json
import re
import os
import sys
import traceback
from typing import Dict
from typing import Any
from typing import List
from typing import Union
from internbootcamp.bootcamps.bootcamps_v1.language_analysis.bbehhyperbaton.lib.bbeh_hyperbaton.bbeh_hyperbaton_generator import HyperbatonGenerator
from internbootcamp.bootcamps.bootcamps_v1.language_analysis.bbehhyperbaton.lib.bbeh_hyperbaton.bbeh_hyperbaton_solver import HyperbatonSolver
from internbootcamp.bootcamps.bootcamps_v1.language_analysis.bbehhyperbaton.lib.bbeh_hyperbaton.bbeh_hyperbaton_validor import HyperbatonValidator




class BbehhyperbatonInstructionGenerator(BaseInstructionGenerator):
    """Bbehhyperbaton Bootcamp指令生成器"""
    
    def __init__(self, **kwargs):
        """
        初始化Bbehhyperbaton指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑

        self.generator = self._generator
        self.solver = self._solver
        self.validator = self._validator
    
    @classmethod
    def case_generator(cls) -> Dict[str, Any]:
        if cls._generator is None:
            raise RuntimeError("Generator not initialized. Create an instance of BBEHHyperbatonbootcamp first.")
        return cls._generator.generate_task()
    
    @staticmethod
    def prompt_func(identity: Dict[str, Any]) -> str:
        question = identity['input']
        prompt = f"""你是一个擅长分析英语形容词顺序的AI助手。请解决以下形容词顺序问题:

问题:
{question}

请仔细分析示例中的形容词顺序规律，并判断哪些选项符合这个规律。

请按以下格式输出你的答案:
最终答案: [你的答案]

注意：答案应该是由正确选项的字母组成的字符串（如"ABC"），如果没有正确选项则输出"K"。
"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

