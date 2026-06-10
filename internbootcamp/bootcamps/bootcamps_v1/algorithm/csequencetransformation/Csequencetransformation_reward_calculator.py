import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re




class CsequencetransformationRewardCalculator(BaseRewardCalculator):
    """Csequencetransformation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        从模型输出中提取最后一个[answer]标签内的内容，并标准化格式。
        """
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        normalized = ' '.join(last_match.split())
        return normalized
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证用户答案是否与正确结果一致。
        """
        n = identity['n']
        try:
            correct = cls.solve(n)
            correct_str = ' '.join(map(str, correct))
            user_str = solution.strip()
            user_str = ' '.join(user_str.split())
            return user_str == correct_str
        except Exception:
            return False
    
    # 其他额外方法

