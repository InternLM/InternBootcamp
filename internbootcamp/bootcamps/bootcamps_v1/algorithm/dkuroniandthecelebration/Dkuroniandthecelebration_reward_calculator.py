import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class DkuroniandthecelebrationRewardCalculator(BaseRewardCalculator):
    """Dkuroniandthecelebration奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        从LLM的回复中提取符合格式的答案。
        """
        import re
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output)
        if not matches:
            return None
        return matches[-1].strip()
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证提取的答案是否正确。
        """
        try:
            solution_int = int(solution)
            return solution_int == identity['root']
        except:
            return False
    
    # 其他额外方法

