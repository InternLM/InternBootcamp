import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class CvotingRewardCalculator(BaseRewardCalculator):
    """Cvoting奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        从模型输出中提取最后一个符合格式的答案。
        """
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        last_match = matches[-1].strip().upper()
        return last_match if last_match in ('D', 'R') else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        严格验证答案准确性。
        """
        return solution == identity['correct_answer']
    
    # 其他额外方法

