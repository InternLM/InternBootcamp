import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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




class BbehhyperbatonRewardCalculator(BaseRewardCalculator):
    """Bbehhyperbaton奖励计算器"""
    
    @classmethod
    def extract_output(cls,output: str) -> Union[str, None]:
        try:
            if not output or output.strip() == "" or "null" in output.lower():
                return None

            # 查找最终答案部分
            answer_match = re.search(r'最终答案:\s*([A-K]+)(?:\n|$)', output, re.MULTILINE)
            if answer_match:
                answer_text = answer_match.group(1).strip().strip('"\'')
                # 验证答案格式是否正确（只包含A-K的字母）
                if re.match(r'^[A-K]+$', answer_text):
                    return answer_text
            return None

        except Exception as e:
            return None
    
    @classmethod
    def _verify_correction(cls, answer: Any, identity: Dict[str, Any]) -> bool:
        if cls._solver is None or cls._validator is None:
            raise RuntimeError(
                "Solver or Validator not initialized. Create an instance of BBEHHyperbatonbootcamp first.")

        test_case = {
            "input": identity["input"],
            "target": identity["target"]
        }

        # 使用验证器验证答案
        validation_result = cls._validator.validate_batch([test_case], [answer])
        return validation_result["detailed_results"][0]["is_correct"]
    
    # 其他额外方法

