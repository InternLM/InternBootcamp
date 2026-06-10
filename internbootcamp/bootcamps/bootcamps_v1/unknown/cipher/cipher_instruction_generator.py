import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import ast
import re
import json
import distance
from internbootcamp.bootcamps.bootcamps_v1.unknown.cipher.lib.bootcamp_utils import catch_print

# === 源文件中的全局变量 ===

cipher_env_dict = {}


class CipherInstructionGenerator(BaseInstructionGenerator):
    """Cipher Bootcamp指令生成器"""
    
    def __init__(self, **kwargs):
        """
        初始化Cipher指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 应用其他配置参数
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @staticmethod
    def prompt_func(question_ori) -> str:
        """
        Process the input_data and return the processed prompt.
        
        Args:
            question_ori: The question to be processed.
        
        Returns:
            str: The processed prompt.
        """
        instruction_following = """
Let's think step by step and output the final answer with an example markdown formatting:
Final-answer: ```text
BTWTBIGTKTGBGIKHGTBTBEME
```
"""
        prompt = question_ori + '\n' + instruction_following
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

