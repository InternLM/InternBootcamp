import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import bisect
import random
import re




class DthebestvacationRewardCalculator(BaseRewardCalculator):
    """Dthebestvacation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        从模型输出中提取最后一个[answer]标签内的答案。
        """
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证答案是否正确。
        """
        return solution == identity['correct_answer']
    
    # 其他额外方法

