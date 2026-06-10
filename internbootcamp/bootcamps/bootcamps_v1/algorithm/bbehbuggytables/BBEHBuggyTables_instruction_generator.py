import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import os
from typing import Dict
from typing import Any
from typing import List
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bbehbuggytables.lib.bbeh_buggy_tables.bbeh_buggy_tables_generator import BBEHBuggyTablesGenerator
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bbehbuggytables.lib.bbeh_buggy_tables.bbeh_buggy_tables_solver import BBEHBuggyTablesSolver
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bbehbuggytables.lib.bbeh_buggy_tables.bbeh_buggy_tables_validor import BBEHBuggyTablesValidator




class BbehbuggytablesInstructionGenerator(BaseInstructionGenerator):
    """Bbehbuggytables Bootcamp指令生成器"""
    
    def __init__(self, **kwargs):
        """
        初始化Bbehbuggytables指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 应用其他配置参数
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def case_generator(cls) -> Dict[str, Any]:
        """生成一个新的BBEH Buggy Tables示例"""
        if cls._generator is None:
            raise RuntimeError("Generator not initialized. Create an instance of BBEHBuggyTablesbootcamp first.")
        return cls._generator.generate_example()
    
    @staticmethod
    def prompt_func(identity: Dict[str, Any]) -> str:
        """生成提示语"""
        table_str = json.dumps(identity['input']['table'], indent=2)
        prompt = f"""你是一个擅长处理有bug的表格数据的助手。请解决以下BBEH Buggy Tables问题:

表格数据:
{table_str}

Bug描述: {identity['input']['bug_description']}

查询: {identity['input']['query']}

请根据给定的信息修复表格,并执行查询。给出最终的数值结果,保留两位小数。

请按以下格式输出你的答案:
最终答案: [你的数值结果]
"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

