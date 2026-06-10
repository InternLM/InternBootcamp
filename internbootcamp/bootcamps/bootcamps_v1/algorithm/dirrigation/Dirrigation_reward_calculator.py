import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import bisect
import re




class DirrigationRewardCalculator(BaseRewardCalculator):
    """Dirrigation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """从模型输出中严格提取答案"""
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """严格验证答案，identity即case_generator的输出"""
        return solution == identity.get('answer', None)
    
    # 其他额外方法

