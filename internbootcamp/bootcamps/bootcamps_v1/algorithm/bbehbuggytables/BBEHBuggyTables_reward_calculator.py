import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import os
from typing import Dict
from typing import Any
from typing import List
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bbehbuggytables.lib.bbeh_buggy_tables.bbeh_buggy_tables_generator import BBEHBuggyTablesGenerator
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bbehbuggytables.lib.bbeh_buggy_tables.bbeh_buggy_tables_solver import BBEHBuggyTablesSolver
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bbehbuggytables.lib.bbeh_buggy_tables.bbeh_buggy_tables_validor import BBEHBuggyTablesValidator




class BbehbuggytablesRewardCalculator(BaseRewardCalculator):
    """Bbehbuggytables奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> float:
        """从模型输出中提取答案"""
        try:
            numbers = [float(s) for s in output.split() if s.replace('.', '').isdigit()]
            return numbers[-1] if numbers else None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, answer: float, identity: Dict[str, Any]) -> bool:
        """验证答案是否正确"""
        if cls._solver is None:
            raise RuntimeError("Solver not initialized. Create an instance of BBEHBuggyTablesbootcamp first.")
        expected_result = cls._solver.solve(identity)
        return abs(answer - expected_result) < 1e-6 if answer is not None and expected_result is not None else False
    
    # 其他额外方法

