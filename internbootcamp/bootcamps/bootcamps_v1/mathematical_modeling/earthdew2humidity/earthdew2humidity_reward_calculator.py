import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import json
import numpy as np




class Earthdew2humidityRewardCalculator(BaseRewardCalculator):
    """Earthdew2humidity奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        boxed_start_index = output.find('\\boxed{')
        boxed_end_index = output.rfind('}', boxed_start_index)
        boxed = output[boxed_start_index + 7:boxed_end_index]
        # print(boxed)
        # 提取数字（含小数点）
        number_match = re.findall(r'\d+(?:\.\d+)?', boxed)[-1]
        if number_match:
            try:
                return float(number_match)
            except ValueError:
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, solution: str, identity: dict) -> bool:
        # 解析 LLM 给出的系数 c，形如 “c*x”
        try:
            c = float(solution)
        except:
            return False
        # print(c)
        # 验证 c ≈ k
        return abs(c - identity["humidity"]) < 1e-1
    
    # 其他额外方法

