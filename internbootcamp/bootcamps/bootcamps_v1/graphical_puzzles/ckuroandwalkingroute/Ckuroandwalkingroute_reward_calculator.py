import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque
from collections import defaultdict




class CkuroandwalkingrouteRewardCalculator(BaseRewardCalculator):
    """Ckuroandwalkingroute奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        从模型输出中提取最后一个[answer]标签内的整数
        """
        import re
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        try:
            return int(matches[-1])
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证答案是否与预计算的正確答案一致
        """
        return solution == identity['correct_answer']
    
    # 其他额外方法

