import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from typing import Set
from typing import Tuple




class BchemicaltableRewardCalculator(BaseRewardCalculator):
    """Bchemicaltable奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> int:
        """
        增强答案提取的鲁棒性，处理多种格式异常
        """
        # 匹配最后一个合法答案标签
        matches = re.findall(
            r'\[answer\][\s]*([+-]?\d+)[\s]*\[/answer\]', 
            output, 
            re.IGNORECASE
        )
        if not matches:
            return None
        
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution: int, identity: dict) -> bool:
        """
        严格验证答案，含类型检查
        """
        return (
            isinstance(solution, int) and 
            solution == identity['correct_answer']
        )
    
    # 其他额外方法

