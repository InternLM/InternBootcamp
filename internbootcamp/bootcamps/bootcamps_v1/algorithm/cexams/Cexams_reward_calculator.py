import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CexamsRewardCalculator(BaseRewardCalculator):
    """Cexams奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强答案提取鲁棒性"""
        matches = re.findall(
            r'\[answer\s*\]\s*(\d+)\s*\[/answer\s*\]',
            output,
            re.IGNORECASE | re.DOTALL
        )
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """严格验证逻辑"""
        try:
            # 按官方日期排序（核心验证逻辑）
            sorted_exams = sorted(identity['exams'], key=lambda x: x[0])
            last_day = 0
            for a, b in sorted_exams:
                last_day = max(b, last_day) if b >= last_day else a
            return solution == last_day
        except Exception as e:
            print(f"验证异常：{str(e)}")
            return False
    
    # 其他额外方法

