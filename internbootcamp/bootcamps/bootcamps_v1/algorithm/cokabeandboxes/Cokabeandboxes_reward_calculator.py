import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CokabeandboxesRewardCalculator(BaseRewardCalculator):
    """Cokabeandboxes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """从模型输出中提取最后一个[answer]标签内的答案"""
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """验证答案是否正确"""
        try:
            return int(solution) == identity['expected_ans']
        except (ValueError, TypeError):
            return False
    
    # 其他额外方法

