import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CvanyaandexamsRewardCalculator(BaseRewardCalculator):
    """Cvanyaandexams奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 参数解析
        n, r, avg = identity['n'], identity['r'], identity['avg']
        exams = identity['exams']
        
        # 计算理论需求
        required_total = avg * n
        current_total = sum(ai for ai, _ in exams)
        
        # 情况1：初始已达标
        if current_total >= required_total:
            return solution == 0
        
        # 情况2：需要提升
        sorted_exams = sorted(exams, key=lambda x: x[1])
        deficit = required_total - current_total
        essays = 0
        
        for ai, bi in sorted_exams:
            increment = min(r - ai, deficit)
            essays += increment * bi
            deficit -= increment
            if deficit <= 0:
                break
        
        return essays == solution
    
    # 其他额外方法

