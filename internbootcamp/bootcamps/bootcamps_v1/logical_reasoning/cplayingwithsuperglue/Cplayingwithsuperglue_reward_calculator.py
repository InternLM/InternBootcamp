import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CplayingwithsuperglueRewardCalculator(BaseRewardCalculator):
    """Cplayingwithsuperglue奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        增强抽取鲁棒性，忽略大小写匹配
        """
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, flags=re.IGNORECASE)
        if not matches:
            return None
        last_ans = matches[-1].strip().capitalize()
        return last_ans if last_ans in ('First', 'Second') else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        精确复现参考算法的验证逻辑
        """
        # 提取坐标差
        dx = abs(identity['x1'] - identity['x2'])
        dy = abs(identity['y1'] - identity['y2'])
        
        # 按参考算法逻辑处理坐标交换
        if dx > dy:
            dx, dy = dy, dx  # 交换坐标差
        
        # 严格应用判定条件
        is_first_win = (dy <= 4) and (dx + dy <= 6)
        return str(solution).capitalize() == ("First" if is_first_win else "Second")
    
    # 其他额外方法

